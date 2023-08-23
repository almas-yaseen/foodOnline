# Generated by Django 4.2.3 on 2023-08-11 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_coupon_valid_from_remove_coupon_valid_to'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coupon',
            old_name='code',
            new_name='coupoun_code',
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='active',
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='discount',
        ),
        migrations.AddField(
            model_name='coupon',
            name='discount_price',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='coupon',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coupon',
            name='minimum_amount',
            field=models.IntegerField(default=500),
        ),
    ]
