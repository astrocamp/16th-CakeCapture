# Generated by Django 5.0.6 on 2024-06-11 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_alter_ordermethod_store_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermethod',
            name='payment_method',
            field=models.CharField(choices=[('credit_card', '信用卡'), ('line_pay', 'LINE PAY')], default='credit_card', max_length=20),
        ),
    ]
