from datetime import datetime
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView,View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from orders.models import Order,OrderMethod
from .form import OrderForm
from store.models import Product, RelationalProduct
from carts.cart import Cart
from django.contrib import messages  
from orders import ecpay_payment_sdk
import importlib.util
spec = importlib.util.spec_from_file_location(
    "ecpay_payment_sdk",
    "orders/ecpay_payment_sdk.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)





def order_form(request):
    form = OrderForm()
    return render(request, 'orders/order_form.html', {'form': form})

def order_confirm(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.buyer = request.user if request.user.is_authenticated else None
            order.save()  # 先保存 order 获取 id
            today_date = datetime.now().strftime('%Y%m%d') 
            order.order_id = f'{today_date}{order.id:08}'
            order.save(update_fields=['order_id'])
            order.refresh_from_db()
            order.name = request.POST.get('recipient_name')
            order.phone = request.POST.get('recipient_cell_phone')
            order.email = request.POST.get('recipient_email')
            # 处理购物车
            cart = Cart(request)
            totals = cart.cart_total()
            order.total = totals
            order.save()  # 更新总金额
            
            for product_id, quantity in cart.get_quants().items():
                product = Product.objects.get(id=product_id)  # 取得 Product 實例
                RelationalProduct.objects.create(order=order, product=product, number=quantity)
            # 创建 OrderMethod 并关联 Order
            order_method = OrderMethod.objects.create(order=order,user=request.user if request.user.is_authenticated else None,
                delivery_method=request.POST.get('delivery_method'),
                payment_method=request.POST.get('payment_method'),
                coupon_used='coupon' in request.POST,
                store_name=request.POST.get('store_name', ''),
                store_address=request.POST.get('store_address', ''),
                order_name=request.POST.get('order_name'),
                order_cell_phone=request.POST.get('order_cell_phone'),
                order_phone=request.POST.get('order_phone', ''),
                order_email=request.POST.get('order_email'),
                recipient_name=request.POST.get('recipient_name'),
                recipient_cell_phone=request.POST.get('recipient_cell_phone'),
                recipient_email=request.POST.get('recipient_email'),
                invoice_option=request.POST.get('invoice_option'),
                invoice_number=request.POST.get('invoice_number', ''),
                return_agreement='return_agreement' in request.POST
            )

                # 传递 Order 和 OrderMethod 给下个页面
            return render(request, 'orders/order_confirm.html', {
                'order': order,
                'order_method': order_method,
                'cart_products': cart.get_prods(),
                'quantities': cart.get_quants(),
                'totals': totals
            })
        else:
            messages.error(request, '請檢查輸入的資料。')
            return redirect('orders:order_form')
    else:
        form = OrderForm()
        return render(request, 'home.html')



class ConfirmView(TemplateView):
    template_name = 'cart/cart_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.request.session.get('order_id')
        return context


class ECPayView(TemplateView):
    template_name = "orders/ecpay.html"

    def post(self, request, *args, **kwargs):
        scheme = request.is_secure() and "https" or "http"
        domain = request.META['HTTP_HOST']

        order_id = request.POST.get("order_id")
        order = Order.objects.get(order_id=order_id)
        product_list = "#".join(
            [product.name for product in order.product.all()])
        order_params = {
            'MerchantTradeNo': order.order_id,
            'StoreID': '',
            'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            'PaymentType': 'aio',
            'TotalAmount': order.total,
            'TradeDesc': order.order_id,
            'ItemName': product_list,
            # ReturnURL為付款結果通知回傳網址，為特店server或主機的URL，用來接收綠界後端回傳的付款結果通知。
            'ReturnURL': f'{scheme}://{domain}/orders/return/',
            'ChoosePayment': 'ALL',
            # 消費者點選此按鈕後，會將頁面導回到此設定的網址(返回商店按鈕)
            'ClientBackURL': f'{scheme}://{domain}/',
            'ItemURL': f'{scheme}://{domain}/products/',  # 商品銷售網址
            'Remark': '交易備註',
            'ChooseSubPayment': '',
            # 消費者付款完成後，綠界會將付款結果參數以POST方式回傳到到該網址
            'OrderResultURL': f'{scheme}://{domain}/orders/order_result',
            'NeedExtraPaidInfo': 'Y',
            'DeviceSource': '',
            'IgnorePayment': '',
            'PlatformID': '',
            'InvoiceMark': 'N',
            'CustomField1': '',
            'CustomField2': '',
            'CustomField3': '',
            'CustomField4': '',
            'EncryptType': 1,
        }
        # 建立實體
        ecpay_payment_sdk = module.ECPayPaymentSdk(
            MerchantID='3002607',
            HashKey='pwFHCqoQZGmho4w6',
            HashIV='EkRm7iFT261dpevs'
        )
        # 產生綠界訂單所需參數
        final_order_params = ecpay_payment_sdk.create_order(order_params)

        # 產生 html 的 form 格式
        action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
        # action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
        ecpay_form = ecpay_payment_sdk.gen_html_post_form(
            action_url, final_order_params)
        context = self.get_context_data(**kwargs)
        context['ecpay_form'] = ecpay_form
        return self.render_to_response(context)


class ReturnView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ReturnView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ecpay_payment_sdk = module.ECPayPaymentSdk(
            MerchantID='3002607',
            HashKey='pwFHCqoQZGmho4w6',
            HashIV='EkRm7iFT261dpevs'
        )
        res = request.POST.dict()
        back_check_mac_value = request.POST.get('CheckMacValue')
        check_mac_value = ecpay_payment_sdk.generate_check_value(res)
        if check_mac_value == back_check_mac_value:
            return HttpResponse('1|OK')
        return HttpResponse('0|Fail')



@csrf_exempt
def order_result(request):
    if request.method == 'POST':
        ecpay_payment_sdk = module.ECPayPaymentSdk(
            MerchantID='3002607',
            HashKey='pwFHCqoQZGmho4w6',
            HashIV='EkRm7iFT261dpevs'
        )
        res = request.POST.dict()
        back_check_mac_value = request.POST.get('CheckMacValue')
        order_id = request.POST.get('MerchantTradeNo')
        rtnmsg = request.POST.get('RtnMsg')
        rtncode = request.POST.get('RtnCode')
        check_mac_value = ecpay_payment_sdk.generate_check_value(res)

        if check_mac_value == back_check_mac_value and rtnmsg == 'Succeeded' and rtncode == '1':
            order = Order.objects.get(order_id=order_id)
            order.status = 'waiting_for_shipment'
            order.save()

            return render(request,'orders/order_success.html')

        return render(request, 'orders/order_fail.html')

    return HttpResponse("Invalid request method", status=405)


