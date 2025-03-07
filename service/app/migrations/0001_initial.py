# Generated by Django 5.1.6 on 2025-03-07 17:14

import app.models
import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('delivered', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tid', models.BigIntegerField(unique=True)),
                ('full_name', models.CharField(blank=True, max_length=1024, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=1024, null=True)),
                ('address', models.CharField(blank=True, max_length=1024, null=True)),
                ('balance', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=1024)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_images')),
                ('price', models.IntegerField()),
                ('quantity', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('category', models.ForeignKey(default=app.models.Category.get_empty_category, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='app.category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('final_cost', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('is_paid', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='app.user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('total_cost', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='carts', to='app.payment')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='carts', to='app.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='carts', to='app.user')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
