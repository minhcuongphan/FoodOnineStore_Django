$(document).ready(function() {
    const $languageSelect = $('#language-select');

    // Function to update the class based on the selected value
    function updateLanguageClass() {
        const selectedValue = $languageSelect.val();
        $languageSelect.removeClass('en vi'); // Remove existing language classes
        $languageSelect.addClass(selectedValue); // Add the new language class
    }

    // Initialize the correct class on page load
    updateLanguageClass();

    // Update the class whenever the value changes
    $languageSelect.on('change', function () {
        updateLanguageClass();
    });

    $('.add_to_cart').on('click', function(e) {
        e.preventDefault();
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            data: {
                food_id: food_id
            },
            success: function(response) {
                handleErrorMessages(response);
                $('#cart_counter').html(response.cart_counter['cart_count']);
                $('#qty-' + food_id).html(response.qty);

                applyCartAmounts(
                    response.cart_amounts['subtotal'],
                    response.cart_amounts['tax_dict'],
                    response.cart_amounts['grandtotal']
                );
            }
        })
    })

    //place the cart item quantity on load
    $('.item_qty').each(function () {
        let id = $(this).attr('id');
        let qty = $(this).attr('data-qty');
        $('#'+id).text(qty);
    });

    $('.decrease_cart').on('click', function(e) {
        e.preventDefault();
        food_id = $(this).attr('data-id');
        cart_id = $(this).attr('data-cart-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                handleErrorMessages(response);
                $('#cart_counter').html(response.cart_counter['cart_count']);
                $('#qty-' + food_id).html(response.qty);

                if (window.location.pathname == '/cart/') {
                    removeCartItem(response.qty, cart_id);
                    checkEmptyCart();
                }

                applyCartAmounts(
                    response.cart_amounts['subtotal'],
                    response.cart_amounts['tax_dict'],
                    response.cart_amounts['grandtotal']
                );
            }
        })
    })

    $('.delete_cart').on('click', function(e) {
        e.preventDefault();
        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                handleErrorMessages(response);
                $('#cart_counter').html(response.cart_counter['cart_count']);
                $('#qty-' + cart_id).html(response.qty);
                removeCartItem(0, cart_id);
                checkEmptyCart();
                applyCartAmounts(
                    response.cart_amounts['subtotal'],
                    response.cart_amounts['tax_dict'],
                    response.cart_amounts['grandtotal']
                );
            }
        })
    })

    //apply cart amounts
    function applyCartAmounts(subtotal, tax_dict, grandtotal) {
        if (window.location.pathname == '/cart/') {
            $('#subtotal').html(subtotal);
            $('#total').html(grandtotal);

            for (key1 in tax_dict) {
                for (key2 in tax_dict[key1]) {
                    $("#tax-" + key1).html(tax_dict[key1][key2])
                }
            }
        }
    }

    //check if the cart is empty
    function checkEmptyCart() {
        let cart_counter = $('#cart_counter').text()
        if (cart_counter == 0) {
            $('#empty_cart').removeClass('d-none')
        }
    }

    // delete the cart element if the qty is 0
    function removeCartItem(cartItemQty, cart_id) {
        if (cartItemQty <= 0) {
            $('#cart-item-' + cart_id).remove();
        }
    }

    function handleErrorMessages(response) {
        let options = {};

        if (response.status === 'Failed') {
            options = {
              title: "",
              text: response.message,
              showCancelButton: false,
              confirmButtonColor: "#3085d6",
              confirmButtonText: "Ok",
            };

            if (response.error_type === 'login_required') {
              options.icon = "warning";
              options.onClose = () => {
                window.location = '/login';
              };
            } else {
              options.icon = "error";
            }
        }

        if (response.status === 'Success') {
            options = {
                title: "",
                text: response.message,
                icon: "success"
            };
        }

        Swal.fire(options);
    }

    $('.add_hour').on('click', function(e) {
        e.preventDefault();
        let day = $('#id_day').val();
        let from_hour = $('#id_from_hour').val();
        let to_hour = $('#id_to_hour').val();
        let is_closed = $('#id_is_closed').is(":checked");
        let csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        let url = $('#add_hour_url').val();

        is_closed = is_closed ? "True" : "False";
        condition = is_closed ? "day != ''" : "day != '' && from_hour != '' && to_hour != ''";

        if (!eval(condition)) {
            Swal.fire({
                title: "",
                icon: "info",
                text: "Please fill all fields",
                showCancelButton: false,
                confirmButtonColor: "#3085d6",
                confirmButtonText: "Ok",
            });

            return;
        }

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'day': day,
                'from_hour': from_hour,
                'to_hour': to_hour,
                'is_closed': is_closed,
                'csrfmiddlewaretoken': csrf_token
            },
            success: function(response) {
                handleErrorMessages(response);

                if (response.status == 'Failed') {
                    return;
                }

                let html = ''
                if (response.is_closed == 'Closed') {
                    html = "<tr id='open_hour_" + response.id+ "'>" +
                        "<td><b>" + response.day + "</b></td>" +
                        "<td>Closed</td>" +
                        "<td><a href='#' class='delete_opening_hour' data-id='" + response.id + "' data-url='opening-hours/delete/" + response.id + "'>Remove</a></td>" +
                    "</tr>"
                } else {
                    html = "<tr id='open_hour_" + response.id+ "'>" +
                        "<td><b>" + response.day + "</b></td>" +
                        "<td>" + response.from_hour + " - " + response.to_hour + "</td>" +
                        "<td><a href='#' class='delete_opening_hour' data-id='" + response.id + "' data-url='opening-hours/delete/" + response.id + "'>Remove</a></td>" +
                    "</tr>"
                }

                $('.opening_hours').append(html)
                $('#opening_hours')[0].reset();
            }
        })
    })

    $(document).on('click', '.delete_opening_hour', function(e) {
        e.preventDefault();
        url = $(this).attr('data-url');
        hour_id = $(this).attr('data-id');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                handleErrorMessages(response);
                if (response.status == 'Failed') return;
                $('#open_hour_'+hour_id).remove();
            }
        })
    })

    $('#placeOrderBtn').on('click', function(e) {
        let paymentMethod = $("input[name='payment_method']:checked").val();
        if (!paymentMethod) {
            $('#payment-method-error').html('Please select a payment method');
            return false;
        }
    });

    $("input[name='payment_method']").on('change', function () {
        $('#payment-method-error').html('');
    });

    // Get the CSRF token from the cookie
    function getCSRFToken() {
        let csrfToken = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(function (cookie) {
                const [key, value] = cookie.trim().split('=');
                if (key === 'csrftoken') {
                    csrfToken = decodeURIComponent(value);
                }
            });
        }
        return csrfToken;
    }

    // Delete coupon
    $('.coupon-delete-btn').click(function () {
        var couponId = $(this).data('id');

        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `/coupons/api/delete/${couponId}/`,
                    type: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCSRFToken()
                    },
                    success: function (response) {
                        if (response.success) {
                            Swal.fire(
                                'Deleted!',
                                response.message,
                                'success'
                            ).then(() => {
                                location.reload();
                            });
                        } else {
                            Swal.fire(
                                'Error!',
                                response.message,
                                'error'
                            );
                        }
                    },
                    error: function (xhr) {
                        Swal.fire(
                            'Error!',
                            'An error occurred while deleting the coupon.',
                            'error'
                        );
                    }
                });
            }
        });
    });

    //Discount code verification and apply the discount code
    $('#apply-discount-btn').click(function () {
        // console.log({{ request.user }})
        var discountCode = $('#discount-code').val(); // Get the entered discount code
        var total = $('#total').text(); // Get the current total amount
        var userid = $(this).attr('data-user-id');

        if (!discountCode) {
            $('#discount-code-error').text('Please enter a discount code.');
            return;
        }

        // Clear any previous error messages
        $('#discount-code-error').text('');

        // Send an AJAX request to validate and apply the discount code
        $.ajax({
            url: '/coupons/api/apply/', // Replace with your discount code API endpoint
            type: 'POST',
            data: {
                discount_code: discountCode,
                grandtotal: total,
                'X-CSRFToken': getCSRFToken(),
                userid: userid
            },
            success: function (response) {
                if (response.success) {
                    // Update the total with the discounted amount
                    $('#total').text(response.new_total);
                    Swal.fire('Success!', response.message, 'success');
                } else {
                    // Show error message
                    $('#discount-code-error').text(response.message);
                }
            },
            error: function () {
                Swal.fire('Error!', 'An error occurred while applying the discount code.', 'error');
            }
        });
    });
});