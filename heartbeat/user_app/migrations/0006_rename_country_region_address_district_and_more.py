# Generated by Django 5.0.1 on 2024-04-12 10:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0005_alter_account_date_of_birth_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='country_region',
            new_name='district',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='zip_code',
            new_name='pin_code',
        ),
    ]