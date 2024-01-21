from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from marketplace.models import Cart, Tax
from marketplace.context_processors import get_cart_amounts
from orders.forms import OrderForm
from orders.models import Order, OrderedFood, Payment
import simplejson as json
from collections import defaultdict
from vendors.models import Food
from .utils import generate_order_number
import stripe
from accounts.utils import send_notification
from django.contrib import messages
from django.db.models import Sum


stripe.api_key = settings.STRIPE_SECRET_KEY
BACKEND_DOMAIN = settings.BACKEND_DOMAIN


def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("marketplace")

    vendors_ids = []
    for item in cart_items:
        if item.food.vendor.id not in vendors_ids:
            vendors_ids.append(item.food.vendor.id)

    vendor_subtotal = defaultdict(Decimal)
    for item in cart_items:
        foods = Food.objects.get(pk=item.food.id)
        vendor_id = foods.vendor.id
        subtotal = Decimal(foods.price * item.quantity)
        vendor_subtotal[vendor_id] += subtotal

    total_data = {}
    for vendor_id, vendor_subtotal in vendor_subtotal.items():
        get_tax = Tax.objects.filter(is_active=True)
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * vendor_subtotal) / 100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})

        total_data[vendor_id] = {str(vendor_subtotal): str(tax_dict)}

    total_tax = get_cart_amounts(request)["tax"]
    grand_total = get_cart_amounts(request)["grand_total"]
    tax_data = get_cart_amounts(request)["tax_dict"]

    if request.method == "POST":
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = Order()
            order.first_name = order_form.cleaned_data["first_name"]
            order.last_name = order_form.cleaned_data["last_name"]
            order.phone_number = order_form.cleaned_data["phone_number"]
            order.email = order_form.cleaned_data["email"]
            order.address = order_form.cleaned_data["address"]
            order.country = order_form.cleaned_data["country"]
            order.state = order_form.cleaned_data["state"]
            order.city = order_form.cleaned_data["city"]
            order.pin_code = order_form.cleaned_data["pin_code"]
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()

            data = {
                "order": order,
                "cart_items": cart_items,
            }
            return render(request, "orders/place_order.html", data)

        else:
            for errors in order_form.errors.values():
                for error in errors:
                    messages.error(request, error)

    return render(request, "orders/place_order.html")


def payment(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    total_tax = get_cart_amounts(request)["tax"]
    order_number = request.GET.get("order_number", None)

    items = []
    for item in cart_items:
        items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.food.food_name,
                    },
                    "unit_amount": int(item.food.price * 100),
                },
                "quantity": item.quantity,
            }
        )

    tax_amount_cents = int(total_tax * 100)

    items.append(
        {
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": "Total Tax",
                },
                "unit_amount": tax_amount_cents,
            },
            "quantity": 1,
        }
    )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=items,
        mode="payment",
        success_url=BACKEND_DOMAIN
        + f"/payment/success?session_id={{CHECKOUT_SESSION_ID}}&order_number={order_number}",
        cancel_url=BACKEND_DOMAIN
        + f"/payment/cancel?session_id={{CHECKOUT_SESSION_ID}}&order_number={order_number}",
    )

    return redirect(session.url)


def payment_success(request):
    checkout_session_id = request.GET.get("session_id", None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    transaction_id = session.payment_intent
    order_number = request.GET.get("order_number", None)

    payment = Payment.objects.create(
        user=request.user,
        transaction_id=transaction_id,
        amount=session.amount_total / 100,
        status="Paid",
    )

    order = get_object_or_404(Order, user=request.user, order_number=order_number)
    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    for item in cart_items:
        ordered_food = OrderedFood()
        ordered_food.order = order
        ordered_food.payment = payment
        ordered_food.user = request.user
        ordered_food.food = item.food
        ordered_food.quantity = item.quantity
        ordered_food.price = item.food.price
        ordered_food.amount = item.food.price * item.quantity
        ordered_food.save()

    mail_subject = "Thank you for ordering."
    mail_template = "orders/emails/order_confirmation_email.html"
    context = {
        "user": request.user,
        "order": order,
        "to_email": order.email,
    }
    send_notification(mail_subject, mail_template, context)

    mail_subject = "You have received a new order."
    mail_template = "orders/emails/new_order_received.html"
    to_emails = []
    for item in cart_items:
        if item.food.vendor.user.email not in to_emails:
            to_emails.append(item.food.vendor.user.email)

    context = {
        "user": request.user,
        "order": order,
        "to_email": to_emails,
    }
    send_notification(mail_subject, mail_template, context)

    Cart.objects.filter(user=request.user).delete()

    return redirect(
        "order_complete", order_number=order_number, transaction_id=transaction_id
    )


def payment_cancel(request):
    checkout_session_id = request.GET.get("session_id", None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    transaction_id = session.payment_intent
    order_number = request.GET.get("order_number", None)
    transaction_id = transaction_id or "canceled_payment"

    payment = Payment.objects.create(
        user=request.user,
        transaction_id=transaction_id,
        amount=session.amount_total / 100,
        status="Cancelled",
    )
    order = get_object_or_404(Order, user=request.user, order_number=order_number)
    order.payment = payment
    order.is_ordered = False
    order.save()
    return render(request, "orders/order_cancelled.html")


def order_complete(request, order_number, transaction_id):
    order = Order.objects.get(
        order_number=order_number,
        payment__transaction_id=transaction_id,
        is_ordered=True,
    )
    ordered_foods = OrderedFood.objects.filter(order=order)
    tax_dict = order.tax_data
    tax_dict = json.loads(tax_dict)
    subtotal = ordered_foods.aggregate(Sum("amount"))["amount__sum"] or 0
    data = {
        "order": order,
        "ordered_foods": ordered_foods,
        "transaction_id": transaction_id,
        "tax_dict": tax_dict,
        "subtotal": subtotal,
    }
    return render(request, "orders/order_complete.html", data)
