from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.decorators import api_view
from .models import MenuItem
from .serializers import MenuItemSerializer

# Create your views here.
class MenuItemView(APIView):
    def get(self, request):
        MenuItems = MenuItem.objects.all()
        serializer = MenuItemSerializer(MenuItems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API endpoint for restaurant menu.
# GET is used to return menu as API.
# @api_view(['GET']) 
# def get_menu(request):
#     menu = [
#         {
#             "name":"Paneer Butter Masala",
#             "description": "Cottage cheese in a rich tomato-based gravy",
#             "price":220.00 
#         },
#         {
#             "name":"Chicken Biryani",
#             "description": "Frangrant rice cooked with marinated chicken and spices",
#             "price":250.00
#         }
#     ]
#     return Response(menu)