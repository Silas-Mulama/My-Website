import django.contrib.auth.forms
from .models import Room,Message,User
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm


 

class createRoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ('__all__')
        exclude = ['host','participants']
        
class updateMessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ([ 'body'])

class UserForm(ModelForm):
    
    class Meta:
        model = User
        fields = ['image','name','username','email','bio']
     
class UserRegForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['name','username','email','password1','password2']
     
