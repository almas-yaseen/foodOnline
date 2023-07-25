from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import User,Userprofile
@receiver(post_save,sender=User)
def post_save_create_profile_reciever(sender,instance,created,**kwargs):
    print(created)
    if created:
        Userprofile.objects.create(user=instance)
 
    else:
        try:
            profile = Userprofile.objects.get(user=instance)
            profile.save()
      
        except:
            # create userprofile not exist 
            Userprofile.objects.create(user=instance)
      
   
  
@receiver(pre_save,sender=User)
def pre_save_profile_reciever(sender,instance,**kwargs):
    pass
    
               