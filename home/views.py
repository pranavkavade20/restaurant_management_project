from django.shortcuts import render
import requests

# Home page
def home(request):
    return render(request,'home/index.html')

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

