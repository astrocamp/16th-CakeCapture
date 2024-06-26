from django.contrib.auth.models import User
from django.db import models
from products.models import Product
from datetime import datetime
from transitions import Machine
from django.db.models.signals import post_save
from django.dispatch import receiver


DELIVERY_CHOICES = [
    ("pick_up", "自取"),
    ("home_delivery", "宅配到府"),
]

PAYMENT_CHOICES = [
    ("ECPay", "綠界支付"),
    ("line_pay", "LINE Pay"),
]


class Order(models.Model):
    order_id = models.CharField(max_length=20, unique=True, blank=True)
    email = models.EmailField(max_length=50)
    name = models.CharField(max_length=10)
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=50)
    used_coupon = models.ForeignKey(
        "accounts.UserCoupon",
        related_name="user_coupon",
        null=True,
        on_delete=models.SET_NULL,
    )
    address = models.CharField(max_length=255)
    total = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    product = models.ManyToManyField(
        "products.Product", related_name="order_set", through="products.RelationalProduct")
    status = models.CharField(max_length=100, choices=(("unpaid", "未付款"), ("payment_fail", "付款失敗"), ("waiting_for_shipment", "準備出貨"), (
        "transporting", "運送中"), ("completed", "訂單已完成"), ("cancelled", "訂單已取消"), ("waiting_for_check", "訂單待確認")), default="waiting_for_check")

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        states = ['waiting_for_check', 'unpaid', 'payment_fail', 'waiting_for_shipment', 'transporting', 'completed', 'cancelled']
        transitions = [
            {'trigger': 'confirm', 'source': 'waiting_for_check',
                'dest': 'unpaid', 'after': 'update_status'},
            {'trigger': 'fail', 'source': 'waiting_for_check',
                'dest': 'payment_fail', 'after': 'update_status'},
            {'trigger': 'pay', 'source': 'waiting_for_check',
                'dest': 'waiting_for_shipment', 'after': 'update_status'},
            {'trigger': 'pay', 'source': 'unpaid',
                'dest': 'waiting_for_shipment', 'after': 'update_status'},
            {'trigger': 'fail', 'source': 'unpaid',
                'dest': 'payment_fail', 'after': 'update_status'},
            {'trigger': 'ship', 'source': 'waiting_for_shipment',
                'dest': 'transporting', 'after': 'update_status'},
            {'trigger': 'ship', 'source': 'waiting_for_check',
                'dest': 'transporting', 'after': 'update_status'},
        ]

        self.machine = Machine(
            model=self, states=states, transitions=transitions, initial="waiting_for_check")

    def update_status(self):
        self.status = self.state
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.order_id:
            today_date = datetime.now().strftime("%Y%m%d")
            self.order_id = f"{today_date}{self.id:08}"
            super().save(update_fields=["order_id"])


class OrderMethod(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="ordermethod"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    delivery_method = models.CharField(
        max_length=20, choices=DELIVERY_CHOICES, default="home_delivery"
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, default="ECPay"
    )
    store_name = models.CharField(max_length=100, blank=True)
    store_address = models.CharField(
        max_length=200, blank=True, default="10046 台北市中正區衡陽路 7 號 5 樓"
    )
    order_name = models.CharField(max_length=50)
    order_cell_phone = models.CharField(max_length=10)
    order_address = models.CharField(max_length=200, blank=True)
    order_email = models.EmailField(max_length=50)
    recipient_name = models.CharField(max_length=50)
    recipient_cell_phone = models.CharField(max_length=10)
    recipient_address = models.CharField(max_length=200)
    recipient_email = models.EmailField(max_length=50)
    return_agreement = models.BooleanField(default=False)

    def __str__(self):
        return self.order_name


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(default=0)
    item_total = models.IntegerField(default=0)

    def __str__(self):
        return f"OrderItem - {str(self.id)}"
