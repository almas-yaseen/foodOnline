from django.shortcuts import get_object_or_404, render,redirect
from marketplace.models import Cart,Coupon
from decimal import Decimal
from vendor.views import get_vendor
from django.template.loader import get_template
from xhtml2pdf import pisa
from marketplace.context_processors import get_cart_amounts
from io import BytesIO
from reportlab.pdfgen import canvas
from .forms  import OrderForm
from accounts.models import User
from django.http import HttpResponse,JsonResponse
from .models import Order,OrderedFood,FoodItem
from marketplace.models import Tax
from orders.models import OrderedFood,FoodItem
from .models import Payment
from vendor.models import Vendor
import simplejson as json
from .utils import generate_order_number
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
import razorpay
from foodOnline_main.settings import RZP_KEY_ID,RZP_KEY_SECRET
client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

# Create your views here.



def apply_coupon(request):
    print('Coupon starts')
    if request.method == 'POST':
        data = {}
        body = json.loads(request.body)
        coupon_code = body.get('coupon')
        print(coupon_code)
        total_price = body.get('total_price')
        print(total_price)

        try:
            coupon = Coupon.objects.get(coupon_code__iexact=coupon_code, is_expired=False)
        except Coupon.DoesNotExist:
            data['message'] = 'Not a Valid Coupon'
            data['total'] = total_price
        else:
            if coupon.is_expired:
                data['message'] = 'Coupon Already Used'
                data['total'] = total_price
            else:
                minimum_amount = coupon.minimum_amount
                discount_price = coupon.discount_price
                print(discount_price)
                if total_price >= minimum_amount:
                    total_price -= discount_price
                    request.session['total'] = total_price
                    coupon.is_expired = True
                    coupon.save()
                    print(total_price)
                    data['message'] = f'{coupon.coupon_code} Applied'
                    data['total'] = total_price 
                    print(data)
                else:
                    data['message'] = 'Not a Valid Coupon'
                    data['total'] = total_price
                    print('else')
                    print(data)

        return JsonResponse(data)


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)
    
    # {"vendor_id":{"subtotal":{"tax_type": {"tax_percentage": "tax_amount"}}}}
    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    total_data = {}
    k = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            k[v_id] = subtotal
    
        # Calculate the tax_data
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage) : str(tax_amount)}})
        # Construct total data
        total_data.update({fooditem.vendor.id: {str(subtotal): str(tax_dict)}})
    

        

    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save() # order id/ pk is generated
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()

            # RazorPay Payment
            DATA = {
                "amount": float(order.total) * 100,
                "currency": "INR",
                "receipt": "receipt #"+order.order_number,
                "notes": {
                    "key1": "value3",
                    "key2": "value2"
                }
            }
            rzp_order = client.order.create(data=DATA)
            rzp_order_id = rzp_order['id']

            context = {
                'order': order,
                'cart_items': cart_items,
                'rzp_order_id': rzp_order_id,
                'RZP_KEY_ID': RZP_KEY_ID,
                'rzp_amount': float(order.total) * 100,
            }
            return render(request, 'orders/place_order.html', context)

        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')



@login_required(login_url='login')
def payments(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        order_number = request.POST.get('order_number')
        transaction_id= request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        order = Order.objects.get(user=request.user,order_number=order_number)
        payment = Payment ( 
                           user = request.user,
                           transaction_id = transaction_id,
                           payment_method = payment_method,
                           amount = order.total,
                           status = status
                           )
        payment.save()
        order.payment = payment
        order.is_ordered = True 
        order.save()
        
        
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food =  OrderedFood()
            ordered_food.order = order
            ordered_food.payment =  payment 
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity
            ordered_food.save()
        
        mail_subject = 'Thank you for ordering with us '
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user':request.user,
            'order':order,
            'to_email':order.email
            
        }
        send_notification(mail_subject,mail_template,context)
        
        mail_subject = 'You have recieved new order'
        mail_template = 'orders/new_order_recieved.html'
        to_emails =[]
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)
        print('to_emails=>', to_emails)
        
        context = { 
                   'order':order,
                   'to_email':to_emails,
                   
                   }
        
        
        send_notification(mail_subject,mail_template,context)
        
        response = {
            
            'order_number':order_number,
            'transaction_id':transaction_id,
        }
        
        cart_items.delete()
        return JsonResponse(response)
  
    return HttpResponse('payment view')   


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    try:
        order = Order.objects.get(order_number=order_number,payment__transaction_id=transaction_id,is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal +=(item.price * item.quantity)
        
        tax_data = json.loads (order.tax_data)
        print(tax_data)   
        context = {
            'order':order,
            'ordered_food':ordered_food,
            'subtotal':subtotal,
            'tax_data':tax_data,
            
        }
        return render(request,'orders/order_complete.html',context)
    except:
        return redirect('home')
    
    

def users(request):
    users = User.objects.all()
    return render(request,'myusers.html',{'users':users})

def block_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            print("jacky")
            user = User.objects.get(username=username)
            user.is_active = False
            user.save()
            return JsonResponse({'status': 'success', 'message': 'User blocked successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
    else:
        print("not")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def unblock_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            user.is_active = True
            user.save()
            return JsonResponse({'status': 'success', 'message': 'User unblocked successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    


@login_required(login_url='login')
def myorder_status(request):
    ordered_food = OrderedFood.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user,is_ordered=True)
    context = {
        'orders':orders,
        'ordered_food':ordered_food,
    }
    return render(request,'myorder_status.html',context)




def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user == order.user and order.status == 'Pending':
        order.status = 'Cancelled'
        order.save()
        # Add any other actions you need here, such as refunding payment, sending notifications, etc.
    return redirect('myorder_status')





def download_order_pdf(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, user=request.user, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        template = get_template('orders/order_pdf_template.html')  # Replace with the correct template path
        context = {
            'order': order,
            'ordered_food': ordered_food,
        }
        html = template.render(context)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order_number}.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error generating PDF', content_type='text/plain')

        return response

    except Order.DoesNotExist:
        return HttpResponse("The requested order does not exist.")
    except Exception as e:
        return HttpResponse(f"An error occurred while generating the PDF: {e}")
