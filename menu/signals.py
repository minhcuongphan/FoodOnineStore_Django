from django.db.models.signals import pre_save
from django.dispatch import receiver
from menu.models import FoodItem
from simple_history.utils import update_change_reason

# @receiver(pre_save, sender=FoodItem)
# def handle_fooditem_history(sender, instance, **kwargs):
#     # Check if the instance already exists in the database
#     if instance.pk:
#         # Get the current state of the model (old values)
#         old_instance = FoodItem.objects.filter(pk=instance.pk).first()
#         if not old_instance:
#             return  # If the old instance doesn't exist, exit early

#         # Set a change reason for the historical record
#         update_change_reason(instance, "Updated FoodItem")
#     else:
#         # For new instances, set a change reason for the initial state
#         update_change_reason(instance, "Created FoodItem")