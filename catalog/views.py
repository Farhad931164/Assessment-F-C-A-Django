import random

import pandas as pd
from django.shortcuts import render
from django.views import generic
from django.db.models import Sum, Q
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import django.contrib.auth
from django.contrib.auth.models import User


from .models import Book, Availability, Wishlist
from .forms import BookSearch


@require_http_methods(["GET"])
def index(request):
    num_books = Book.objects.all().count()
    all_books = Availability.objects.aggregate(Sum("total_copies", default=0))[
        "total_copies__sum"
    ]
    total_available = Availability.objects.aggregate(
        Sum("available_copies", default=0)
    )["available_copies__sum"]

    context = {
        "num_books": num_books,
        "all_books": all_books,
        "total_available": total_available,
    }
    return render(request, "index.html", context=context)


class BookListView(generic.ListView):
    paginate_by = 20
    template_name = "book_list.html"

    def get_queryset(self):
        title = self.request.GET.get("title")
        author = self.request.GET.get("author")
        filters = Q()
        
        if title:
            filters &= Q(title__contains=title)

        if author:
            filters &= Q(authors__contains=author)

        return Book.objects.all().filter(filters)


def books_search(request):
    must_redirect = ("author" in request.GET.keys()) or ("title" in request.GET.keys())
    author = request.GET.get("author", "")
    title = request.GET.get("title", "")

    if must_redirect:
        return redirect(reverse("books") + f"?author={author}&title={title}")

    context = {"form": BookSearch()}
    return render(request, "book_search.html", context=context)


def filldb(request):
    Book.objects.all().delete()

    df = pd.read_csv("books_data.csv")

    name_map = {
        "Id": "book_id",
        "ISBN": "isbn",
        "Authors": "authors",
        "Publication Year": "publication_year",
        "Title": "title",
        "Language": "language",
    }

    for _, row in df.iterrows():
        new_record = {name_map[column]: row[column] for column in row.keys()}
        book = Book.objects.create(**new_record)
        total_copies = random.randint(1, 5)
        available_copies = random.randint(-total_copies, total_copies)

        # Give more chance to cases where book is not available to borrow
        available_copies = 0 if available_copies < 0 else available_copies

        # Let's add some random availability
        Availability.objects.create(
            book=book, total_copies=total_copies, available_copies=available_copies
        )
        
    return redirect(index)


@require_http_methods(["GET", "POST"])
def wishlist(request, book_id):
    user = django.contrib.auth.get_user(request)
    book = Book.objects.get(book_id=book_id)
    Wishlist.objects.create(user = user, book = book)
    return redirect('books')


@require_http_methods(["GET", "POST"])
def borrow(request, book_id):
    return redirect('books')

def logout(request):
    django.contrib.auth.logout(request)
    return redirect(index)
