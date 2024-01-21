$(document).ready(function () {
  $(".add_to_cart").on("click", function (e) {
    e.preventDefault();
    food_id = $(this).attr("data-id");
    url = $(this).attr("data-url");
    data = {
      food_id: food_id,
    };
    $.ajax({
      type: "GET",
      url: url,
      data: data,
      success: function (response) {
        if (response.status == "Login_required") {
          Swal.fire(response.message, "", "info").then(function () {
            window.location = "/login";
          });
        } else if (response.status == "Failed") {
          Swal.fire(response.message, "", "error");
        } else {
          $("#cart_counter").html(response.cart_counter["cart_count"]);
          $("#qty-" + food_id).html(response.qty);

          if (window.location.pathname == "/marketplace/cart/") {
            applyCartAmounts(
              response.cart_amounts["subtotal"],
              response.cart_amounts["tax_dict"],
              response.cart_amounts["grand_total"]
            );
          }
        }
      },
    });
  });

  $(".item_qty").each(function () {
    let id = $(this).attr("id");
    let qty = $(this).attr("data-qty");
    $("#" + id).html(qty);
  });

  $(".minus_from_cart").on("click", function (e) {
    e.preventDefault();
    food_id = $(this).attr("data-id");
    cart_id = $(this).attr("id");
    url = $(this).attr("data-url");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        if (response.status == "Login_required") {
          Swal.fire(response.message, "", "info").then(function () {
            window.location = "/login";
          });
        } else if (response.status == "Failed") {
          Swal.fire(response.message, "", "error");
        } else {
          $("#cart_counter").html(response.cart_counter["cart_count"]);
          $("#qty-" + food_id).html(response.qty);
          if (window.location.pathname == "/marketplace/cart/") {
            deleteCartItem(response.qty, cart_id);
            checkEmptyCart();
            applyCartAmounts(
              response.cart_amounts["subtotal"],
              response.cart_amounts["tax_dict"],
              response.cart_amounts["grand_total"]
            );
          }
        }
      },
    });
  });

  $(".delete_cart_item").on("click", function (e) {
    e.preventDefault();
    cart_id = $(this).attr("data-id");
    url = $(this).attr("data-url");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        if (response.status == "Failed") {
          Swal.fire(response.message, "", "error");
        } else {
          $("#cart_counter").html(response.cart_counter["cart_count"]);
          Swal.fire(response.status, response.message, "success");

          if (window.location.pathname == "/marketplace/cart/") {
            deleteCartItem(0, cart_id);
            checkEmptyCart();
            applyCartAmounts(
              response.cart_amounts["subtotal"],
              response.cart_amounts["tax_dict"],
              response.cart_amounts["grand_total"]
            );
          }
        }
      },
    });
  });

  function deleteCartItem(itemQty, cart_id) {
    if (itemQty <= 0) {
      document.getElementById("item-" + cart_id).remove();
    }
  }

  function checkEmptyCart() {
    let cart_counter = document.getElementById("cart_counter").innerHTML;
    if (cart_counter == 0) {
      document.getElementById("empty_cart").style.display = "block";
    }
  }

  function applyCartAmounts(subtotal, tax_dict, grand_total) {
    $("#subtotal").html(subtotal);
    $("#total").html(grand_total);

    for (key1 in tax_dict) {
      for (key2 in tax_dict[key1]) {
        $("#tax-" + key1).html(tax_dict[key1][key2]);
      }
    }
  }
});

$(document).ready(function () {
  $(document).on("click", ".add_hours", function (e) {
    e.preventDefault();
    let day = document.getElementById("id_day").value;
    let from_hour = document.getElementById("id_from_hour").value;
    let to_hour = document.getElementById("id_to_hour").value;
    let is_closed = document.getElementById("id_is_closed").checked;
    let csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    let url = document.getElementById("opening_hours_url").value;

    if (is_closed) {
      is_closed = "True";
      condition = "day != ''";
    } else {
      is_closed = "False";
      condition = "day != '' && from_hour != '' && to_hour != ''";
    }

    if (eval(condition)) {
      $.ajax({
        type: "POST",
        url: url,
        data: {
          day: day,
          from_hour: from_hour,
          to_hour: to_hour,
          is_closed: is_closed,
          csrfmiddlewaretoken: csrf_token,
        },
        success: function (response) {
          if (response.status == "Success") {
            if (response.is_closed == "Closed") {
              html =
                "<tr id='opening-hours-" +
                response.id +
                "'><td>" +
                response.day +
                "</td><td>Closed</td><td>Closed</td><td><a href='' class='delete_hours' data-url='/vendor/opening-hours/delete/" +
                response.id +
                "'>Delete</a></td></tr>";
            } else {
              html =
                "<tr id='opening-hours-" +
                response.id +
                "'><td>" +
                response.day +
                "</td><td>" +
                response.from_hour +
                "</td><td>" +
                response.to_hour +
                "</td><td><a href='' class='delete_hours' data-url='/vendor/opening-hours/delete/" +
                response.id +
                "'>Delete</a></td></tr>";
            }

            $("#opening_hours").append(html);
            document.getElementById("opening_hours_form").reset;
          } else {
            Swal.fire(response.message, "", "error");
          }
        },
      });
    } else {
      Swal.fire("Please, fill up all fields", "", "info");
    }
  });

  $(document).on("click", ".delete_hours", function (e) {
    e.preventDefault();
    url = $(this).attr("data-url");
    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        if (response.status == "Success") {
          document.getElementById("opening-hours-" + response.id).remove();
        }
      },
    });
  });
});

$(document).ready(function () {
  if (
    window.location.pathname == "/" ||
    window.location.pathname == "/vendor/vendor-profile/" ||
    window.location.pathname == "/customer/customer-profile/"
  ) {
    $("#id_address")
      .autocomplete({
        source: function (request, response) {
          $.ajax({
            url: "https://nominatim.openstreetmap.org/search",
            dataType: "json",
            data: {
              q: request.term,
              format: "json",
              limit: 5,
            },
            success: function (data) {
              handleAutocompleteResults(data, response);
            },
          });
        },
        minLength: 2,
        select: function (event, ui) {
          $("#id_address").val(ui.item.value);
          $("#id_latitude").val(ui.item.lat);
          $("#id_longitude").val(ui.item.lon);
          return false;
        },
      })
      .autocomplete("instance")._renderItem = function (ul, item) {
      return $("<li>")
        .append("<div>" + item.label + "</div>")
        .appendTo(ul);
    };

    function handleAutocompleteResults(data, response) {
      var suggestions = $.map(data, function (item) {
        return {
          label: item.display_name,
          value: item.display_name,
          lat: item.lat,
          lon: item.lon,
        };
      });

      var suggestionsElement = $("#autocomplete-suggestions");
      suggestionsElement.empty();

      if (suggestions.length > 0) {
        var ul = $("<ul>");
        $.each(suggestions, function (index, item) {
          ul.append($("<li>").text(item.label));
        });
        suggestionsElement.append(ul);

        ul.find("li").on("click", function () {
          $("#id_address").val($(this).text());
          $("#id_latitude").val(suggestions[$(this).index()].lat);
          $("#id_longitude").val(suggestions[$(this).index()].lon);
          suggestionsElement.empty();
        });

        suggestionsElement.show();
      } else {
        suggestionsElement.hide();
      }
    }

    document
      .getElementById("search_form")
      .addEventListener("submit", function (event) {
        var radiusSelect = document.getElementsByName("radius")[0];
        if (radiusSelect.value === "Choose Radius") {
          Swal.fire("Please choose a radius.", "", "info");
          event.preventDefault();
        }
      });
  }
});
