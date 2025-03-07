from django.db import models
from django.core.validators import MinValueValidator
from uuid import uuid4
# Create your models here.

class Base(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: abstract = True


class User(Base):
    tid = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=1024, blank=True, null=True)
    phone_number = models.CharField(max_length=1024, blank=True, null=True)
    address = models.CharField(max_length=1024, blank=True, null=True)

    balance = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    @property
    def personal_data(self):
        return (self.full_name and self.phone_number and self.address)

    async def get_purchase_amount(self):
        total_cost = await Cart.objects.filter(user=self).aaggregate(models.Sum('total_cost'))
        return total_cost.get('total_cost__sum')


class Category(Base):
    EMPTY_CATEGORY = 'empty'

    name = models.CharField(max_length=1024)

    def __str__(self): return f'{self.name}'

    @classmethod
    def get_empty_category(cls):
        obj, _ = cls.objects.get_or_create(name=cls.EMPTY_CATEGORY)
        return obj


class Product(Base):
    name = models.CharField(max_length=1024)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images', null=True, blank=True)
    price = models.IntegerField()
    quantity = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, default=Category.get_empty_category,
        related_name='products'
    )

    def __str__(self): return f'{self.name}'


class Cart(Base):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='carts')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='carts')
    total_cost = models.IntegerField(validators=[MinValueValidator(0)])
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    is_paid = models.BooleanField(default=False)


