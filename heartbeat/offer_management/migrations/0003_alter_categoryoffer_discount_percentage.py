# Generated by Django 5.0.1 on 2024-05-14 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offer_management', '0002_alter_categoryoffer_discount_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryoffer',
            name='discount_percentage',
            field=models.DecimalField(decimal_places=0, max_digits=5),
        ),
    ]