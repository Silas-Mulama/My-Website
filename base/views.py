from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from easylearn.settings import EMAIL_HOST_USER
from .forms import createRoomForm,updateMessageForm,UserForm,UserRegForm
from base.models import Room,Topic,Message,User
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .token import account_activation_token

# Create your views here.
def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.order_by('-created').filter(Q(name__icontains=q)|Q(topic__name__icontains=q))[0:3]
    rooms_count = len(Room.objects.all())
    topics = Topic.objects.all()[0:4]
    room_messages = Message.objects.all().filter(Q(room__name__icontains=q))[0:3]
    context = {'rooms': rooms,'topics':topics,'rooms_count':rooms_count,'room_mess':room_messages}
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def create_room(request):
    topics= Topic.objects.all()
    form = createRoomForm
    if request.method == 'POST':
        form = createRoomForm(request.POST)
        topic_name = request.POST['topic']
        topic,created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST['name'],
            description=request.POST['description']
        )
        messages.success(request,'Room Created Successfully!!')
        return redirect('home')
    else:
        form = createRoomForm()
    context = {'form': form,'topics':topics}
    return render(request, 'base/room.html', context)


def display_room(request, pk):
    room = get_object_or_404(Room, id=pk)
    Messages = room.message_set.all().order_by('-created')
    Participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user =request.user,
            room = room,
            body = request.POST['comment']
        )
        room.participants.add(request.user)
        return redirect('room-room', pk=room.id)
    context = {'room':room,'Messages':Messages,'participants':Participants}
    return render(request, 'base/room_details.html',context)


@login_required(login_url='login')
def update_room(request,pk):
    room = get_object_or_404(Room,id=pk)

    if request.user != room.host:
        messages.warning(request,'You are not the owner of this room!!')
        return redirect('home')
    # form = createRoomForm(instance = room)
 
    if request.method == 'POST':
    
        name = request.POST['group-name']
        info = request.POST['group-info']
        
        
        room.name=name
        room.description = info
        room.save()
        messages.success(request,'Room Updated Successfully!!')
        return redirect('home')
    context = {'room':room}
    return render(request,'base/update_room.html',context)

@login_required(login_url='login')
def delete_room(request,pk):
    room = get_object_or_404(Room,id=pk)
    if request.user != room.host:
        return HttpResponse('You are not the owner of this room!!')
    if request.method == 'POST':
        room.delete()
        messages.success(request,'Room Deleted Successfully!!')
        return redirect('home')
    return render(request,'base/delete.html',{'OBJECT':room})

def user_profile(request,pk):
    if request.user.is_authenticated:
        user = get_object_or_404(User, id=pk)
        rooms = user.room_set.all()[:2]
        room_messages = user.message_set.all()[:4]
        topics = Topic.objects.all()
        context = {'user':user,'rooms':rooms,'topics':topics,'room_mess':room_messages}
        return render(request,'base/profile.html',context)
    else:
        return redirect('login')
def login_user(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request,'Username does not exists!!')
        user = authenticate(request,email=email,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,'login success!')
            return redirect('home')
        
        else:
            messages.error(request,'Username or password does not exists!!')
            
    context = {'page':page}
    return render(request,'base/login_register.html',context)

def logout_user(request):
    logout(request)
    messages.success(request, 'Logged Out successfully!!')
    return redirect('home')


def register_user(request):
    page = 'register'
    form = UserRegForm()
    if request.method == 'POST':
        form = UserRegForm(request.POST)
      
        if form.is_valid():
            user = form.save(commit=False)
            full = user.name.split()
            user.first_name = full[0]
            user.last_name = full[1]
            user.username = user.username.lower()
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()
            
            # send welcome email
            message = render_to_string('email.html', {'user': user})
            email = user.email # Assuming the user object has an email attribute
            send_mail(
                'Welcome to EduQuest',
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            
            #send activation link
            # Assuming 'request' and 'user' are available in your context
            current_site = get_current_site(request)
            domain = '192.168.0.16:1000'  # Replace with your local network IP and port
            protocol = 'http'  # Change to 'https' if using HTTPS
            mail_subject = 'Activate your account.'
            message = render_to_string('activation_email.html', {
                'user': user,
                'domain': domain,
                'protocol': protocol,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            send_mail(mail_subject, message, 'settings.EMAIL_HOST_USER', [to_email], fail_silently=False)
            
            messages.success(request, 'Please confirm your email address to complete the registration')
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
            return redirect('register')

    context = {'form': form}
    return render(request, 'base/login_register.html', context)
            
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been confirmed.')
        return redirect('home')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('home')

def update_profile(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    context = {'form':form}
    return render(request,'base/edit-user.html',context)


def delete_message(request,pk):
    message = get_object_or_404(Message,id=pk)
    if request.user != message.user:
        return HttpResponse('You are not the owner of this room!!')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'OBJECT':message})

def update_message(request,pk):
    message = get_object_or_404(Message,id=pk)
    if request.user != message.user:
        messages.warning(request,'You are not the owner of this room!!')
        return redirect('home')
    form = updateMessageForm(instance = message)
    if request.method == 'POST':
        form = updateMessageForm(request.POST,instance = message)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request,'base/updatemess.html',context)


def topics_page(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(
        Q(name__icontains=q))
    topics_all = Topic.objects.all()
    topics_count = topics_all.count()
    context= {'topics':topics,'topics_count':topics_count}
    return render(request,'base/topics.html',context)

def rooms_page(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(name__icontains=q)).order_by('-created')
    rooms_count = rooms.count()
    context= {'rooms':rooms,'rooms_count':rooms_count}
    return render(request,'base/rooms.html',context)
def activitiess_page(request):
    room_messages = Message.objects.all()
    context= {'room_mes':room_messages}
    return render(request,'base/activity.html',context)
