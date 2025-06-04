from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('books_search/', views.books_search, name='books_search'),    
    path('wishlists/<int:book_id>', views.wishlist, name='wishlist'),
    path('borrows/<int:book_id>', views.borrow, name='borrow'),
    path('filldb/', views.filldb, name='filldb'),
    path('logout/', views.logout, name = 'logout')
    ]