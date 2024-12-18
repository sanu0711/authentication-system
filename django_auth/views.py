from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from captcha.fields import CaptchaField
from captcha.helpers import captcha_image_url, captcha_audio_url
from captcha.models import CaptchaStore

from django_auth.forms import LoginForm


def sign_up(request):
    if request.method == 'POST':
        fname = request.POST['first_name']
        lname = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('sign_up')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('sign_up')
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('sign_up')
        user = User.objects.create_user(
            username=username, 
            password=password1, 
            email=email, 
            first_name=fname, 
            last_name=lname
            )
        user.save()
        
        messages.success(request, "Your account has been created successfully!")
        return redirect('sign_in')

    return render(request, 'django_auth/sign_up.html')

def sign_in(request):
    
    captcha_key = CaptchaStore.generate_key()
    captcha_image = captcha_image_url(captcha_key)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        captcha_value = request.POST['captcha_1']
        captcha_hash_key = request.POST['captcha_0']

        user = authenticate(request, username=username, password=password)
        try:
            captcha = CaptchaStore.objects.get(hashkey=captcha_hash_key)
            if not captcha.response == captcha_value.lower():
                messages.error(request, "Incorrect CAPTCHA.")
                return redirect('sign_in')
            else:
                captcha.delete()
        except CaptchaStore.DoesNotExist:
            messages.error(request, "Invalid CAPTCHA.")
            return redirect('sign_in')

        # If user is authenticated and CAPTCHA is valid
        if user is not None:
            login(request, user)
            messages.success(request, "You have logged in successfully!")
            return redirect('home')
        else:
            # Handle invalid login attempts
            if not User.objects.filter(username=username).exists():
                messages.error(request, "User does not exist.")
            else:
                messages.error(request, "Incorrect password.")
            return redirect('sign_in')
    return render(request, 'django_auth/sign_in.html', {
        'captcha_key': captcha_key,
        'captcha_image': captcha_image,
       
    })
    
def change_password(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to change your password.")
        return redirect('sign_in')
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = request.user
        if not user.check_password(old_password):
            messages.error(request, "Incorrect old password.")
            return redirect('change_password')
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('change_password')
        user.set_password(new_password)
        user.save()
        messages.success(request, "Password changed successfully!")
        return redirect('sign_in')
    return render(request, 'django_auth/change_password.html')
    
def sign_out(request):
    logout(request)
    messages.success(request, "You have logged out successfully!")
    return redirect('sign_in')

def home(request):
    return render(request, 'home.html')