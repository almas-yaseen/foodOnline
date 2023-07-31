from django.shortcuts import render
from .forms import UserForm
from django.shortcuts import redirect
from django.contrib.auth.tokens import default_token_generator 
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from .models import User,Userprofile
from vendor.forms import VendorForm
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages,auth
from .utils import detectUser,send_verification_email
from django.core.exceptions import PermissionDenied
from django.conf import settings
from vendor.models import Vendor

# Create your views here. restrict user from accessing the customer page

#restrict customer accessing vendor page  
def check_role_vendor(user):
    if user.role ==1:
        return True
    else:
        raise PermissionDenied
    
#restricting vendor accessing customer page 

def check_role_customer(user):
    if user.role ==2:
        return True 
    else:
        raise PermissionDenied
        





def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in')
        return redirect('dashboard')
    elif request.method =="POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role = User.CUSTOMER
            user.save()
            
            #SEND VERIFICATION 
            mail_subject = 'please activate your account'
            email_template = 'accounts/emails/account_verfication_email.html'
            send_verification_email(request,user,mail_subject,email_template)
            
  
            messages.success(request,'Your account has been registered sucessfully')
            return redirect('registerUser')  
        else:
            print("invalid")
            print(form.errors) 
    else:
        form =UserForm()
    context = {
        'form':form,
    }
    return render(request,'accounts/registerUser.html',context)

def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in')
        return redirect('dashboard')
    elif request.method == "POST":
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST,request.FILES)
        if form.is_valid() and v_form.is_valid:
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            
            user_profile = Userprofile.objects.get(user=user)
            print(user_profile,"ksanckasnjkasnkjad")
            vendor.user_profile  = user_profile
            vendor.save()
            #send verification
            mail_subject = 'please activate your account'
            email_template = 'accounts/emails/account_verfication_email.html'
            send_verification_email(request,user,mail_subject,email_template)
            messages.success(request,'Your account has been registered')
            return redirect('registerVendor')
        else:
            print("invalid forms")
            print(form.errors)
    
    else:
        form = UserForm()
        v_form = VendorForm()
        
        
    form = UserForm()
    v_form = VendorForm()
    context = {
        'form':form,
        'v_form':v_form,
    }
    return render(request,'accounts/registerVendor.html',context)



def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active =True
        user.save()
        messages.success(request,'Congratulation your account has activate')
        return redirect('myaccount')
    else:
        messages.error(request,"invalid activation link")
        return redirect('myaccount')
    


def login(request):
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in')
        return redirect('myaccount')
    elif request.method=="POST":
        email=request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            auth.login(request,user)
            messages.success(request,"You are logged in")
            print("you logged in sflcsldfvnsjdfnjdfkv")
            return redirect('myaccount')

        else:
            messages.error(request,"invalid login credentials")
            print("you are error skljfnkjdfv")
            return redirect('login')
        
    return render(request,'accounts/login.html')
def logout(request):
    auth.logout(request)
    messages.info(request,'you are logged out')
    return redirect('login')

@login_required(login_url='login')
def myaccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custdashboard(request):
    return render(request,'accounts/custdashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendordashboard(request):
    return render(request,'accounts/vendordashboard.html')

def forgot_password(request):
    if request.method == "POST":
        email=request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            #send reset password email
            mail_subject = 'Reset your password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request,user,mail_subject,email_template)
            messages.success(request,'Password reset linke has sent you email address')
            return redirect('login')
        else:
            messages.error(request,'sorry error occurs does not exist your account')
            return redirect('forgot_password')
            
            
    return render(request,'accounts/forgot_password.html')

def reset_password_validate(request,uidb64,token):
    #validate the usser by decoing 
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.info(request,'please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request,'This link has expired')
        return redirect('myaccount')

def reset_password(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            pk = request.session.get('uid')
            user =User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request,'Password reset successfully')
            return redirect('login')
            
            
        else:
            messages.error(request,"Password do not match")
            return redirect('reset_password')
            
        
    return render(request,'accounts/reset_password.html')
