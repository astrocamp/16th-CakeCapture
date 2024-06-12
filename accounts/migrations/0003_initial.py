# Generated by Django 5.0.6 on 2024-06-12 03:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_initial'),
        ('coupons', '0001_initial'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercoupon',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usercoupons_accounts', to='orders.order'),
        ),
        migrations.AddField(
            model_name='usercoupon',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile'),
        ),
        migrations.AddField(
            model_name='profile',
            name='coupon',
            field=models.ManyToManyField(related_name='profiles', through='accounts.UserCoupon', to='coupons.coupon'),
        ),
    ]