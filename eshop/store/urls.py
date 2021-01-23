from django.urls import path
from  .import views
from .views import Login, Index, Cart, CheckOut, OrderView
urlpatterns = [
    path('', Index.as_view(), name='homepage'),
    path('signup/', views.signup, name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('cart/', Cart.as_view(), name='cart'),
    path('checkout', CheckOut.as_view(), name='checkout'),
    path('orders/', OrderView.as_view(), name='orders'),
]