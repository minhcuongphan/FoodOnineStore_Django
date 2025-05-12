from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Coupon

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