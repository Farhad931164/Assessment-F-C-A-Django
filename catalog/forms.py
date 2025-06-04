import datetime as dt

from django import forms


from .models import Book, Availability, Wishlist, AmazonLink


class BookSearch(forms.Form):
    title = forms.CharField(required=False)
    author = forms.CharField(required=False)
