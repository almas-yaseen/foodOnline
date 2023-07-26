from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import User,Userprofile
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
               