$(document).ready(function() {
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
                    response.cart_amounts['tax'],
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
                    response.cart_amounts['tax'],
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
                    response.cart_amounts['tax'],
                    response.cart_amounts['grandtotal']
                );
            }
        })
    })

    //apply cart amounts
    function applyCartAmounts(subtotal, tax, grandtotal) {
        if (window.location.pathname == '/cart/') {
            $('#subtotal').html(subtotal);
            $('#tax').html(tax);
            $('#total').html(grandtotal);
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
});