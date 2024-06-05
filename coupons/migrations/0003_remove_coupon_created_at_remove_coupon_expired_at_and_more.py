# Generated by Django 5.0.6 on 2024-06-05 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='expired_at',
        ),
        migrations.AddField(
            model_name='usercoupon',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usercoupon',
            name='expired_at',
            field=models.DateTimeField(blank=True, default=None),
            preserve_default=False,
        ),
    ]
