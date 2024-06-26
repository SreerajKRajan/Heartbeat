# Generated by Django 5.0.1 on 2024-04-19 06:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method_name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=100, null=True)),
                ('shipping_address', models.TextField()),
                ('additional_discount', models.IntegerField(default=0, null=True)),
                ('grand_total', models.IntegerField(default=0, null=True)),
                ('order_note', models.CharField(blank=True, max_length=100, null=True)),
                ('order_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('order_status', models.CharField(choices=[('New', 'New'), ('Accepted', 'Accepted'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled Admin', 'Cancelled Admin'), ('Cancelled User', 'Cancelled User'), ('Returned', 'Returned')], default='New', max_length=20)),
                ('ip', models.CharField(blank=True, max_length=50)),
                ('is_ordered', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_variant', models.CharField(max_length=255, null=True)),
                ('product_id', models.CharField(max_length=255, null=True)),
                ('quantity', models.IntegerField()),
                ('product_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('grand_totol', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('images', models.ImageField(upload_to='media/order/images')),
                ('ordered', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order_status', models.CharField(choices=[('New', 'New'), ('Accepted', 'Accepted'), ('Delivered', 'Delivered'), ('Shipped', 'Shipped'), ('Cancelled_Admin', 'Cancelled Admin'), ('Cancelled_User', 'Cancelled User'), ('Returned', 'Returned'), ('Return Status', 'Returned Status'), ('Return Approved', 'Returned Approved'), ('Return Rejected', 'Returned Rejected')], default='New', max_length=20)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='order.order')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('amount_paid', models.CharField(max_length=30)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('FAILED', 'Failed'), ('SUCCESS', 'Success')], max_length=20)),
                ('is_paid', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('payment_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.paymentmethod')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.payment'),
        ),
        migrations.CreateModel(
            name='ReturnRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='return_requests', to='order.orderproduct')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
