# Generated by Django 4.2.3 on 2023-08-11 04:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_rename_code_coupon_coupoun_code_remove_coupon_active_and_more'),
        ('marketplace', '0003_alter_tax_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='copoun',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.coupon'),
        ),
    ]
