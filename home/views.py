from django.shortcuts import render
import requests

def menu_view(request):
    try:
        response = requests.get('http://localhost:8000/api/products/menu/')
        menu_data = response.json()
    except Exception as e:
        menu_data=[]
    
    return render(request, 'home/menu.html',{'menu':menu_data})

