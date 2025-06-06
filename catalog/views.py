import random

import pandas as pd
from django.shortcuts import render
from django.views import generic
from django.db.models import Sum, Q, Count, ExpressionWrapper, DurationField, Avg, F
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import django.contrib.auth
from django.contrib.auth.models import User


from .models import Book, Availability, Wishlist, Borrows
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

    total_with_customer = Borrows.objects.aggregate(Count("book"))["book__count"]

    completed_borrowings = Borrows.objects.filter(returned__isnull=False)
    borrowings_with_duration = completed_borrowings.annotate(
        duration=ExpressionWrapper(
            F("returned") - F("created"), output_field=DurationField()
        )
    )
    avg_duration_result = borrowings_with_duration.aggregate(
        average_lending_duration=Avg("duration")
    )
    average_time = avg_duration_result.get("average_lending_duration")

    average_time_display = "N/A"
    if average_time:
        total_seconds = average_time.total_seconds()
        days = average_time.days
        hours = int(total_seconds // 3600) % 24
        minutes = int(total_seconds // 60) % 60
        average_time_display = f"{days} days, {hours} hours, {minutes} minutes"

    context = {
        "num_books": num_books,
        "all_books": all_books,
        "total_available": total_available,
        "total_with_customer": total_with_customer,
        "average_lending": average_time_display,
    }

    return render(request, "index.html", context=context)


class BookListView(generic.ListView):
    paginate_by = 20
    template_name = "book_list.html"

    def get_queryset(self):
        # generic query to return all books or by search term
        user = django.contrib.auth.get_user(self.request)
        title = self.request.GET.get("title")
        author = self.request.GET.get("author")
        search_type = self.request.GET.get("search_type")

        filter_type = Q.AND if search_type == "1" else Q.OR

        filters = Q()

        if title:
            filters.add(Q(title__contains=title), filter_type)

        if author:
            filters.add(Q(authors__contains=author), filter_type)

        qset = Book.objects.all().filter(filters)
        for book in qset:
            book.is_wishlisted = book.wishlisted_by.filter(user=user).exists()
            book.is_borrowed = book.borrowed_by.filter(user=user).exists()

        return qset


@require_http_methods(["GET"])
def books_search(request):
    # this both provides the book search form and also redirect for actual search
    must_redirect = ("author" in request.GET.keys()) or ("title" in request.GET.keys())
    author = request.GET.get("author", "")
    title = request.GET.get("title", "")
    search_type = request.GET.get("search_type")

    if must_redirect:
        return redirect(
            reverse("books")
            + f"?author={author}&title={title}&search_type={search_type}"
        )

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
    # here if record exists, we just remove it, like toggeling
    # The standard way is to have a POST and DELETE but I didn't want to write AJAX and html doesn't support DELETE for forms
    user = django.contrib.auth.get_user(request)
    book = Book.objects.get(book_id=book_id)

    wobj = Wishlist.objects.filter(user=user, book=book)

    if wobj:
        wobj.delete()
    else:
        Wishlist.objects.create(user=user, book=book)

    return redirect("books")


@require_http_methods(["POST", "DELETE"])
def borrow(request, book_id):
    if request.method == "POST":
        user = django.contrib.auth.get_user(request)
        book = Book.objects.get(book_id=book_id)

        if book.availability.available_copies > 0:  # if a book is available to be lend
            if (
                not book.borrowed_by.all().filter(user=user.id).exists()
            ):  # if user has not borrowed the same book before
                aobj = Availability.objects.get(book=book)
                aobj.available_copies -= 1
                aobj.save()

                Borrows.objects.create(book=book, user=user)

    return redirect("books")


def logout(request):
    django.contrib.auth.logout(request)
    return redirect(index)
