from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Coupon
from django.http import JsonResponse
from marketplace.context_processors import get_cart_amounts
from django.contrib.auth.decorators import login_required

@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def delete_coupon_api(request, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id)
        coupon.delete()
        return Response({'success': True, 'message': 'Coupon deleted successfully.'}, status=status.HTTP_200_OK)
    except Coupon.DoesNotExist:
        return Response({'success': False, 'message': 'Coupon not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def apply_discount_code(request):
    discount_code = request.data.get('discount_code')
    grandtotal = float(request.data.get('grandtotal'))
    userid = int(request.data.get('userid'))

    try:
        coupon = Coupon.objects.get(code=discount_code, active=True)
        if coupon.discount_type == 'percentage':
            discount = float(grandtotal * (coupon.amount / 100))
        else:  # Fixed amount discount
            discount = float(coupon.amount)

        new_total = max(grandtotal - discount, 0)  # Ensure total is not negative
        # Store the discount code and new total in the session
        request.session[f'discount_code_{userid}'] = discount_code
        request.session[f'temp_grandtotal_{userid}'] = new_total

        return JsonResponse({'success': True, 'new_total': new_total, 'message': 'Discount applied successfully!'})
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid or expired discount code.'})