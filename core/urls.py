from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('user-profile', views.UserProfile.as_view(), name='user-profile'),

    # Items and Categories
    path('item_list', views.ItemList.as_view(), name="item_list"),
    path('item_detail/<slug>/', views.ItemDetail.as_view(), name="item_detail"),
    path('item_update/<slug>/', views.ItemPartialUpdateView.as_view(), name="item_update"),
    path('category_list', views.CategoryList.as_view(), name="category_list"),
    path('category_detail/<slug>/', views.CategoryDetail.as_view(), name="category_detail"),
    path('login-redirect-url', views.LoginRedirectIntermediary.as_view(),name="login-redirect-url"),
    path('item-available', views.ItemAvailableView.as_view(),name="item-available"),

    # Address
    path('address-list', views.AddressListView.as_view(),name="address-list"),
    path('address-update', views.AddressPartialUpdateView.as_view(),name="address-update"),
    path('address-detail/<int:pk>/', views.AddressDetailView.as_view(),name="address-detail"),

    # Cart
    path('cart-item-price/', views.CartItemsPriceView.as_view(),name="cart-item-price"),
    path('user-orders', views.UserOrders.as_view(), name='user-orders'),
    path('all-orders', views.AllOrders.as_view(), name='all-orders'),
    path('orders-status-update', views.OrderStatusUpdate.as_view(), name='orders-status-update'),
    path('create-order', views.CreateOrderView.as_view(),name="create-order"),
    path('complete-order', views.CompleteOrderView.as_view(),name="complete-order"),

    #table order
    path('table-orders-status-update', views.TableOrderStatusUpdate.as_view(), name='table-orders-status-update'),
    path('all-table-orders', views.AllTableOrders.as_view(), name='all-table-orders'),
    path('all-active-table-orders', views.AllActiveTableOrders.as_view(), name='all-active-table-orders'),
    path('all-inactive-table-orders', views.AllInactiveTableOrders.as_view(), name='all-inactive-table-orders'),
    path('table-orders-staff-status-update', views.TableOrderStatusStaffUpdate.as_view(), name='table-orders-staff-status-update'),
    path('deliver-orders', views.AllOrders.as_view(), name='deliver-orders'),
    path('user-logout', views.api_logout.as_view(), name='user-logout'),
    path('cancel-order', views.CancelOrderView.as_view(), name='cancel-order'),
    path('update-order', views.UpdateOrderView.as_view(), name='update-order'),
    path('open-close-restaurant', views.CloseOpenRestaurant.as_view(), name='open-close-restaurant'),
    path('table-order', views.TableOrderView.as_view(), name="table-order"),
    path('table_list', views.TableList.as_view(), name="table_list"),
    path('table_detail/<slug>/', views.TableDetail.as_view(), name="table_detail"),
]