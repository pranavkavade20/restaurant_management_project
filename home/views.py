from django.shortcuts import render
import requests
from django.conf import settings

# Display Restaurant name
def homepage_view(request):
   context ={
    'restaurant_name' : settings.RESTAURANT_NAME,
    'restaurant_phone': settings.RESTAURANT_PHONE
   }
   return render(request,'home/home.html',context)

# View for fetching API Response.
def menu_view(request):
    try:
        # Getting Response throught a URL.
        response = requests.get('http://localhost:8000/api/products/menu/')
        # Saving response in JSON format.
        menu_data = response.json()
    except Exception as e:
        # If exception occur then it save empty response.
        menu_data=[]
    # Render data to frontend.
    return render(request, 'home/menu.html',{'menu':menu_data})

# 404 page
def trigger_404(request):
    return render(request,"404.html", status = 404)

# about page
def about_view(request):
    return render(request,'about.html')