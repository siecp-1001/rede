from os import path
from django.core.mail import send_mail
from django.shortcuts import render, redirect,get_object_or_404
from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import FormView
from main import forms
from django.views.generic.list import ListView
from .forms import  ContactForm
from main import forms,models
from django.shortcuts import get_object_or_404, render
from.models import basketline, product, producttag, Room, Message
import logging
from django.contrib.auth import login ,authenticate
from django.contrib import messages
# offer users a way to add, change, and remove their addresses
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django .views.generic.edit import FormView,CreateView,UpdateView,DeleteView
from django .views.generic.edit import (
     FormView,
     CreateView,
     UpdateView,
     DeleteView,
    )
from . import models
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse

# Create your views here.
def home(request):
    return render(request, "home.html", {})
def about_us(request):
    return render(request, "about_us.html", {})

class Contactusview(FormView):
    template_name="pages/contact_form.html"
    form_class= forms.ContactForm
    success_url="/"
    
    
    def form_valid(self, form) :
        form.send_mail()
        return super().form_valid(form)

    
class productlistview(ListView):
    template_name="pages/product_list.html"
    model = models.product
    paginate_by=7
    context_object_name="products"
    def  get_queryset(self):
      return product.objects.all()[:7]





class roomlistview(ListView):
    template_name="chat.html"
    model = models.Room
    paginate_by=10
    context_object_name="Room"
       
#new

            

logger= logging.getLogger(__name__)

class signupview(FormView):
    template_name="signup.html"
    form_class=forms.Usercreationform
    def get_success_url(self) :
        redirect_to=self.request.GET.get("next","/")
        return redirect_to
    def form_valid(self, form) :
        response=super().form_valid(form)
        form.save()
        email=form.cleaned_data.get("email")
        raw_password=form.cleaned_data.get("password1")
        logger.info(
            "new signup for email =%s through signupview",email
        )
        user=authenticate(email=email,password=raw_password)
        login(self.request,user)
        form.send_mail()
        messages.info(
            self.request,"you signed up succesfully"
        )
        return response
     
class adresslistview(LoginRequiredMixin,ListView):
    model=models.adress
    def get_queryset(self) :
        return self.model.objects.filter(user=self.request.user)
 
 
class adresscreateview(LoginRequiredMixin,CreateView):
     model=models.adress 
     fields=[
         "name",
         "address1",
         "address2",
         "zip_code",
         "city",
         "country",
     ]  
     success_url=reverse_lazy("main:adress_list")
     def form_valid(self, form) :
         obj=form.save(commit=False)
         obj.user=self.request.user
         obj.save()
         return super().form_valid(form)          
class adressupdateview(LoginRequiredMixin,UpdateView):
    model=models.adress 
    fields=[
         "name",
         "address1",
         "address2",
         "zip_code",
         "city",
         "country",
     ]  
    success_url=reverse_lazy("main:adress_list")  
    def get_queryset(self) :
        return self.model.objects.filter(user=self.request.user)
class adressdeleteview(LoginRequiredMixin,DeleteView):
    model=models.adress
    success_url=reverse_lazy("main:adress_list")
    def get_queryset(self) :
        return self.model.objects.filter(user=self.request.user)
   
#create chat here 

def home(request):
    return render(request, 'chat.html')

def room(request, room):
    username = request.GET.get('username')
    room_details = Room.objects.get(name=room)
    return render(request, 'room.html', {
        'username': username,
        'room': room,
        'room_details': room_details
    })

def checkview(request):
    room = request.POST['room_name']
    username = request.POST['username']

    if Room.objects.filter(name=room).exists():
        return redirect('/'+room+'/?username='+username)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/'+room+'/?username='+username)

def send(request):
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value=message, user=username, room=room_id)
    new_message.save()
    return HttpResponse('Message sent successfully')

def getMessages(request, room):
    room_details = Room.objects.get(name=room)

    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages":list(messages.values())})









#end
 
def add_to_basket(request):
    product= get_object_or_404(
        models.product, pk=request.GET.get("product_id")
        
    )    
    basket=request.basket
    if not request.basket:
        if request.user.is_authenticated:
            user=request.user 
        else:
            user=None
        basket =models .basket.objects.create(user=user)
        request.session["basket_id"]=basket.id
    
    basketline,created=models.basketline.objects.get_or_create(
        basket=basket,product=product
    ) 
    if not created:
        basketline.quantity +=1
        basketline.save()
    return HttpResponseRedirect(
        reverse("main:product",args=(product.slug,))
    ) 

def manage_basket(request):
    if not request.basket:
        return render(request, "basket.html", {"formset": None})

    if request.method == "POST":
        formset = forms.BasketLineFormSet(
            request.POST, instance=request.basket
        )
        if formset.is_valid():
            formset.save()
    else:
        formset = forms.BasketLineFormSet(
            instance=request.basket
        )

    if request.basket.is_empty():
        return render(request, "basket.html", {"formset": None})

    return render(request, "basket.html", {"formset": formset})          




#create note web 

class notelistview(LoginRequiredMixin,ListView):
    model=models.notes
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
    
class notecreateview(LoginRequiredMixin,CreateView):
    model=models.notes
    fields=[
        "NOTE",
        "date",
    ]  
    success_url= reverse_lazy("main:notes_list")
    def form_valid(self, form) :
         obj=form.save(commit=False)
         obj.user=self.request.user
         obj.save()
         return super().form_valid(form)    
    

class noteupdateview(LoginRequiredMixin,UpdateView):
    model=models.notes 
    fields=[
        "NOTE",
        "date",
     ]  
    success_url=reverse_lazy("main:notes_list")  
    def get_queryset(self) :
        return self.model.objects.filter(user=self.request.user)   



class notedeleteview(LoginRequiredMixin,DeleteView):
    model=models.notes
    success_url=reverse_lazy("main:notes_list")
    def get_queryset(self) :
        return self.model.objects.filter(user=self.request.user)
        