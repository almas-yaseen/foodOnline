from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import  Point

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user 
    def create_superuser(self,first_name,last_name,username,email,password=None):
     user = self.create_user(
         email=self.normalize_email(email),
         username=username,
         password = password,
         first_name=first_name,
         last_name=last_name,
     )   
     user.is_admin=True
     user.is_active = True
     user.is_staff=True
     user.is_superadmin=True 
     user.save(using=self._db)
     return user
     

class Coupon(models.Model):
    coupoun_code = models.CharField(max_length=50, unique=True)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)
    
    

   

class User(AbstractBaseUser):
    VENDOR = 1
    CUSTOMER = 2
    ROLE_CHOICE = (
        (VENDOR,'Vendor'),
        (CUSTOMER,'Customer'),
    )
    first_name = models.CharField(max_length=100)
    last_name= models.CharField(max_length=100)
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(max_length=100,unique=True)
    phone_number = models.CharField(max_length=12,blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE,blank=True,null=True)
    
    #required 
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']
    objects = UserManager()
    
    def __str__(self):
        return self.email 
    def has_perm(self,perm,obj=None):
        return self.is_admin
    
    def has_module_perms(self,app_label):
        return True 
    
    def get_role(self):
        if self.role == User.VENDOR:
            return 'Vendor'
        elif self.role == User.CUSTOMER:
            return 'Customer'
        else:
            return 'Unknown Role'
    
    

    
class Userprofile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,blank=True,null=True)
    profile_picture = models.ImageField(upload_to='users/profile_picture',blank=True,null=True)
    cover_photo = models.ImageField(upload_to='users/cover_photo',blank=True,null=True)
    address = models.CharField(max_length=250,blank=True,null=True)
    
    country = models.CharField(max_length=15,blank=True,null=True)
    state = models.CharField(max_length=15,blank=True,null=True)
    city = models.CharField(max_length=50,blank=True,null=True)
    pin_code = models.CharField(max_length=6,blank=True,null=True)
    latitude = models.CharField(max_length=20,blank=True,null=True)
    location = gismodels.PointField(blank=True,null=True,srid=4326)
    longitude = models.CharField(max_length=20,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    # def full_address(self):
    #     return f'{self.address_line_1},{self.address_line_2}'
    
    
    def __str__(self):
        return self.user.email
    
    def save(self,*args,**kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude),float(self.latitude))
            return super(Userprofile,self).save(*args,**kwargs)
        return super(Userprofile,self).save(*args,**kwargs)
        

            
@receiver(post_save,sender=User)
def post_save_create_profile_reciever(sender,instance,created,**kwargs):
    print(created)
    if created:
        Userprofile.objects.create(user=instance)
        print("user profile created")
    else:
        try:
            profile = Userprofile.objects.get(user=instance)
            profile.save()
            print("User is updated")
        except:
            # create userprofile not exist 
            Userprofile.objects.create(user=instance)
            print("profile was not exist but i create one")
   
  
@receiver(pre_save,sender=User)
def pre_save_profile_reciever(sender,instance,**kwargs):
    print(instance.username,"this user being is")
               
    
    

# post_save.connect(post_save_create_profile_reciever,sender=User)

    