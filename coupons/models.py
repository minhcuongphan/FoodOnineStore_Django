from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=20,
        choices=(
            ('percentage', 'Percentage'),
            ('fixed_amount', 'Fixed Amount')
        ),
        default='percentage'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    max_uses = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of times this coupon can be used."
    )
    used_count = models.PositiveIntegerField(default=0)
    min_cart_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Minimum cart value to apply this coupon.",
        default=0
    )
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.code