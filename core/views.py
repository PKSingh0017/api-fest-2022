from django.shortcuts import render
from rest_framework import generics
from . import models as store_models
from .serializers import ItemSerializer,CategorySerializer,AddressSerializer, UserSerializer, OrderSerializer, TableSerializer, TableOrderSerializer
from django.views.generic import View
from django.http import HttpResponseRedirect
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import (
        SAFE_METHODS, IsAuthenticated, IsAuthenticatedOrReadOnly, 
        BasePermission, IsAdminUser, DjangoModelPermissions, AllowAny
    )
from allauth.account.views import SignupView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework import status
from . import models as core_models
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from rest_framework.pagination import PageNumberPagination
from core.pagination import PaginationHandlerMixin

from core import serializers
class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

# class AccountSignupView(SignupView):
#     def POST()

def home(request):
    return render(request, 'core/home.html')

class ItemList(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = store_models.Item.objects.all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        queryset = store_models.Item.objects.all()
        category_slug = self.request.query_params.get('category')
        if category_slug is not None:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

class TableList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = store_models.Table.objects.all()
    serializer_class = TableSerializer

    # def get_queryset(self):
    #     queryset = store_models.Item.objects.all()
    #     category_slug = self.request.query_params.get('category')
    #     if category_slug is not None:
    #         queryset = queryset.filter(category__slug=category_slug)
    #     return queryset

class TableDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    queryset = store_models.Table.objects.all()
    serializer_class = TableSerializer
    lookup_field = 'slug'

class CategoryList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = store_models.Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = store_models.Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class ItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    queryset = store_models.Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'slug'

class LoginRedirectIntermediary(View):
    """
    Decides where a newly logged in user should go based on the request.
    """
    def get(self, request, *args, **kwargs):
        # url = 'https://urbantandoor.in/landing_page{}'
        next_redirect_url = request.GET.get('next')
        if next_redirect_url:
            url = next_redirect_url
        else:
            url = request.session["next_URL"]
        if not url:
            url = 'https://urbantandoor.in/landing_page{}'
        refresh = RefreshToken.for_user(request.user)
        str1 = "?access_token=" + str(refresh.access_token)
        str2 = "&refresh_token=" + str(refresh)

        # return HttpResponseRedirect(url.format(str1+str2), request)
        return HttpResponseRedirect(url + str1 + str2)

class AdminLoginView(APIView):
    
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:

            curr_user = User.objects.get(username=username)

            if user.is_superuser:
                # refresh = RefreshToken.for_user(curr_user)

                tokens = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                refresh = RefreshToken.for_user(request.user)
                return Response(tokens, status=HTTP_200_OK)
            
            # if user.is_superuser:
            #     return Response({"message": "user is a superuser"}, status=HTTP_200_OK)
            # else:
            #     return Response({"message": "You are not an admin"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "User does not exist"}, status=HTTP_400_BAD_REQUEST)

class ItemAvailableView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({"message": "Invalid data"}, status=HTTP_400_BAD_REQUEST)
        curr_item = core_models.Item.objects.get(slug=slug)
        if curr_item.is_available:
            curr_item.is_available = False
            curr_item.save()
            return Response({"message": "The Item is no longer available now!"}, status=HTTP_200_OK)
        else:
            curr_item.is_available = True
            curr_item.save()
            return Response({"message": "The Item is available now!"}, status=HTTP_200_OK)

class ItemPartialUpdateView(GenericAPIView, UpdateModelMixin):
    permission_classes = [IsAuthenticatedOrReadOnly]
    '''
    You just need to provide the field which is to be modified.
    '''
    queryset = core_models.Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'slug'

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class CreateOrderView(GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request, *args, **kwargs):
        items = request.data.get('items', None)
        order_qs = core_models.Order.objects.filter(
            user=request.user, ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            order.items.all().delete()
        else:
            order = core_models.Order.objects.create(user=request.user)
        for item in items:
            order_item = core_models.OrderItem.objects.create(
                user=request.user,
                item = core_models.Item.objects.get(slug=item["slug"]),
                quantity=item["quantity"],
            )
            order.items.add(order_item)
        return Response({"message": ""},status=HTTP_200_OK)

class CompleteOrderView(GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request, *args, **kwargs):
        try:
            user_order = core_models.Order.objects.get(
                user=request.user,
                ordered=False
            )
            address_id = request.data.get('address_id')
            user_order.address = core_models.Address.objects.get(id=address_id)
            cash_on_delivery = int(request.data.get("cash_on_delivery"))
            user_order.amount = user_order.get_total()
            if cash_on_delivery:
                user_order.cash_on_delivery=True
                user_order.ordered = True
                user_order.ordered_date = timezone.now()
                user_order.status = 'Ordered'
                user_order.save()
                context = {
                    'curr_order': OrderSerializer(user_order).data,
                    'message': "Order created!"
                }
                return Response(context, status=HTTP_200_OK)
            else:
                user_order.cash_on_delivery = False
                user_order.save()
                context = {
                    'curr_order': OrderSerializer(user_order).data,
                    'message': "Please Complete the payment!"
                }
                return Response(context, status=HTTP_200_OK)
            
        except:
            return Response({"message": "You have no active order!"}, status=HTTP_400_BAD_REQUEST)

class CartItemsPriceView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        cart_item_ids = request.GET.get("cart_item_ids")
        cart_item_ids = cart_item_ids.split("*")

        context = {}
        if cart_item_ids:
            for id in cart_item_ids:
                print(id)
                try:
                    context[id] = ItemSerializer(core_models.Item.objects.get(id=int(id))).data
                except:
                    continue
        else:
            context = {}
        return Response(context, status=HTTP_200_OK)

# class CartItemsPriceView(GenericAPIView):
#     def get(self, request, *args, **kwargs):
#         cart_item_slugs = request.data.get("cart_item_slugs")
#         context = {}
#         if cart_item_slugs:
#             for slug in cart_item_slugs:
#                 context[slug] = ItemSerializer(core_models.Item.objects.get(slug=slug)).data
#         else:
#             context = {}
#         return Response(context, status=HTTP_200_OK)

class AddressListView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = core_models.Address.objects.filter(user=self.request.user)
        return queryset
    
    def post(self, request, *args, **kwargs):
        new_address = core_models.Address()
        new_address.user = request.user
        new_address.street_address = request.data.get("street_address")
        new_address.apartment_address = request.data.get("apartment_address")
        new_address.email = request.data.get("email")
        new_address.name = request.data.get("name")
        new_address.zip = request.data.get("zip")
        new_address.phone_number = request.data.get("phone_number")
        new_address.save()
        context = {
            'message': 'Address Saved!',
            'address': AddressSerializer(new_address).data,
        }
        return Response(context, status=HTTP_200_OK)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    queryset = store_models.Address.objects.all()
    serializer_class = AddressSerializer

class AddressPartialUpdateView(GenericAPIView, UpdateModelMixin):
    permission_classes = [IsAuthenticatedOrReadOnly]
    '''
    You just need to provide the field which is to be modified.
    '''
    queryset = core_models.Address.objects.all()
    serializer_class = AddressSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
            
from allauth.account.views import LoginView
class CustomLoginView(LoginView):

    def get_context_data(self, *args, **kwargs):
        self.request.session['next_URL'] = self.request.GET.get("next")
        print("NEXT URL: ", self.request.GET.get("next"))
        return super().get_context_data()

class UserProfile(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            default_address_id = core_models.DefaultAddress.objects.get(user=request.user).id
        except:
            default_address_id=0
        context = {
            'default_address_id': default_address_id,
            'curr_user': UserSerializer(request.user).data,
            'all_addreses': AddressSerializer(core_models.Address.objects.filter(user=request.user), many=True).data,
        }
        return Response(context, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        curr_user = request.user
        try:
            curr_user.username = request.data.get("username")
            curr_user.first_name = request.data.get("first_name")
            curr_user.last_name = request.data.get("last_name")
            curr_user.email = request.data.get("email")
            curr_user.save()
        except:
            return Response({"message": "Username already taken"}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "User details updated successfully"}, status=HTTP_200_OK)

class UserOrders(GenericAPIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, *args, **kwargs):
        curr_user_order = core_models.Order.objects.filter(user=request.user, ordered=False)
        all_user_orders = core_models.Order.objects.filter(user=request.user)
        if curr_user_order.exists():
            curr_order = OrderSerializer(curr_user_order[0]).data
        else:
            curr_order = 'No active order'

        context = {
            'curr_order': curr_order,
            'all_orders': OrderSerializer(all_user_orders, many=True).data
        }


        return Response(context, status=HTTP_200_OK)

# class MyListAPI(APIView, PaginationHandlerMixin):
#     pagination_class = BasicPagination
#     serializer_class = DatasetSerializer
#     def get(self, request, format=None, *args, **kwargs):
#         instance = Dataset.objects.all()
#         page = self.paginate_queryset(instance)
#         if page is not None:
#             serializer = self.get_paginated_response(self.serializer_class(page,
#  many=True).data)
#         else:
#             serializer = self.serializer_class(instance, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class AllOrders(GenericAPIView, PaginationHandlerMixin):
    # permission_classes=[IsAdminUser]
    pagination_class = BasicPagination
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        instance = core_models.Order.objects.filter(ordered=True).order_by('-ordered_date')
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(instance, many=True)
        # all_orders = core_models.Order.objects.filter(ordered=True).order_by('-ordered_date')

        context = {
            'all_orders': serializer.data,
        }

        return Response(context, status=HTTP_200_OK)

class OrderStatusUpdate(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        ids = request.data.get('ids', None)
        status = request.data.get('status', None)
        if not request.user.is_staff:
            return Response({"message": "You are not a staff!"}, status=HTTP_400_BAD_REQUEST)
        
        for id in ids:
            if id is None:
                continue
            curr_order = core_models.Order.objects.get(id=id)
            curr_order.status = status
            curr_order.save()
        return Response({"message": f'The orders were marked {status}!'}, status=HTTP_200_OK)

class DeliverOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        if not request.user.is_staff:
            return Response({"message": "You are not a staff!"}, status=HTTP_400_BAD_REQUEST)
        if id is None:
            return Response({"message": "Invalid data"}, status=HTTP_400_BAD_REQUEST)
        curr_order = core_models.Order.objects.get(id=id)
        if curr_order.status=='Delivered':
            curr_order.status = 'Dispached'
            curr_order.save()
            return Response({"message": "Order marked not delivered!"}, status=HTTP_200_OK)
        else:
            curr_order.status = 'Delivered'
            curr_order.save()
            return Response({"message": "Order marked delivered!"}, status=HTTP_200_OK)

class api_logout(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            # logout(request.user)
            Session.objects.all().delete()
            return Response({"message": "User logged out!"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"message": "User is not logged in!"},status=status.HTTP_400_BAD_REQUEST)
        
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        id = request.data.get('id')
        curr_order = core_models.Order.objects.get(id=id)
        if (curr_order.status=='Dispached'):

            return Response({"message": "You cannot cancel this order!"}, status=HTTP_400_BAD_REQUEST)
        else:
            curr_order.status = 'Cancelled'
            curr_order.save()
            return Response({"message": "Order cancelled!"}, status=HTTP_200_OK)


class UpdateOrderView(GenericAPIView, UpdateModelMixin):
    permission_classes = [IsAuthenticatedOrReadOnly]
    '''
    You just need to provide the field which is to be modified.
    '''
    queryset = core_models.Order.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class CloseOpenRestaurant(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        var = core_models.MetaData.objects.get(name='RestaurantOpen')
        if var.status:
            res_status = 'Open'
        else:
            res_status = 'Closed'
        context = {
            'Status': res_status,
        }
        return Response(context, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        var = core_models.MetaData.objects.get(name='RestaurantOpen')
        if var.status:
            var.status = False
        else:
            var.status = True
        var.save()
        return Response(status=HTTP_200_OK)


class TableOrderView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        items = request.data.get('items', None)
        table_slug = request.data.get('table_slug', None)
        curr_table= core_models.Table.objects.get(slug=table_slug)
        if curr_table.is_vacent:
            curr_order = core_models.TableOrder.objects.create(table=curr_table)
            curr_table.is_vacent = False
            curr_table.save()
        else:
            curr_order = core_models.TableOrder.objects.filter(table=curr_table, is_active=True)
            try:
                curr_order = curr_order[0]
            except:
                curr_order = core_models.TableOrder.objects.create(table=curr_table)
                curr_table.is_vacent = False
                curr_table.save()

        for item in items:
            order_item = core_models.OrderItem.objects.create(
                item = core_models.Item.objects.get(slug=item["slug"]),
                quantity=item["quantity"],
            )
            curr_order.items.add(order_item)
            
            curr_order.amount = curr_order.get_total()
            curr_order.save()
        return Response({"message": "Order Created!"},status=HTTP_200_OK)
    
    def get(self, request, *args, **kwargs):
        table_slug = request.GET.get("table")
        curr_table = core_models.Table.objects.get(slug=table_slug)

        order_qs = core_models.TableOrder.objects.filter(table=curr_table, is_active=True)
        if order_qs.exists():
            curr_order = TableOrderSerializer(order_qs[0]).data
            context = {
                'curr_order': curr_order,
                'curr_table': TableSerializer(curr_table).data
            }
            return Response(context, status=HTTP_200_OK)
        else:
            context = {
                'curr_order': 'No active order!',
                'curr_table': TableSerializer(curr_table).data
            }
            return Response(context, status=HTTP_200_OK)

class TableOrderStatusUpdate(APIView):
    def post(self, request, *args, **kwargs):
        ids = request.data.get('ids', None)
        status = request.data.get('status', None)
        
        for id in ids:
            if id is None:
                continue
            curr_order = core_models.TableOrder.objects.get(id=id)
            curr_table = curr_order.table
            if status=='Completed' or status=='Cancelled':
                curr_order.is_active=False
                curr_order.amount = curr_order.get_total()
                curr_table.is_vacent = True
                curr_table.save()
            curr_order.status = status
            curr_order.save()
        return Response({"message": f'The table orders were marked {status}!'}, status=HTTP_200_OK)

class TableOrderStatusStaffUpdate(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
        ids = request.data.get('ids', None)
        status = request.data.get('status', None)
        
        for id in ids:
            if id is None:
                continue
            curr_order = core_models.TableOrder.objects.get(id=id)
            curr_table = curr_order.table
            if status=='Completed' or status=='Cancelled':
                curr_order.is_active=False
                curr_order.amount = curr_order.get_total()
                curr_table.is_vacent = True
                curr_table.save()
            curr_order.status = status
            curr_order.save()
        return Response({"message": f'The table orders were marked {status}!'}, status=HTTP_200_OK)


class AllTableOrders(GenericAPIView):
    

    def get(self, request, *args, **kwargs):
        all_active_table_orders = core_models.TableOrder.objects.filter(is_active=True).order_by('-timestamp')
        all_inactive_table_orders = core_models.TableOrder.objects.filter(is_active=False).order_by('-timestamp')


        context = {
            'all_active_table_orders': TableOrderSerializer(all_active_table_orders, many=True).data,
            'all_inactive_table_orders': TableOrderSerializer(all_inactive_table_orders, many=True).data,
        }

        return Response(context, status=HTTP_200_OK)


class AllActiveTableOrders(GenericAPIView, PaginationHandlerMixin):
    permission_classes=[IsAdminUser]
    pagination_class = BasicPagination
    serializer_class = TableOrderSerializer

    def get(self, request, *args, **kwargs):
        instance = core_models.TableOrder.objects.filter(is_active=True).order_by('-timestamp')
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(instance, many=True)
        # all_orders = core_models.Order.objects.filter(ordered=True).order_by('-ordered_date')

        context = {
            'all_active_table_orders': serializer.data,
        }

        return Response(context, status=HTTP_200_OK)

class AllInactiveTableOrders(GenericAPIView, PaginationHandlerMixin):
    permission_classes=[IsAdminUser]
    pagination_class = BasicPagination
    serializer_class = TableOrderSerializer

    def get(self, request, *args, **kwargs):
        instance = core_models.TableOrder.objects.filter(is_active=False).order_by('-timestamp')
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(instance, many=True)
        # all_orders = core_models.Order.objects.filter(ordered=True).order_by('-ordered_date')

        context = {
            'all_inactive_table_orders': serializer.data,
        }

        return Response(context, status=HTTP_200_OK)


