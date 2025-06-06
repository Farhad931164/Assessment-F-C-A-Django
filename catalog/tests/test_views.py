from datetime import timedelta
import datetime as dt

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum

from catalog.models import Book, Availability, Wishlist, Borrows
from catalog.views import index, BookListView, books_search, filldb, wishlist, borrow


class BaseViewTest(TestCase):
    def setUp(self):
        self.client = Client()  # Initialize a test client

        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpassword1"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword2"
        )
        self.staff_user = User.objects.create_user(
            username="staffuser", password="staffpassword", is_staff=True
        )

        self.client.login(username="testuser1", password="testpassword1")

        # Create boks
        self.book1 = Book.objects.create(
            book_id=101,
            isbn="9780321765723",
            authors="Eric Matthes",
            publication_year=2019,
            title="Python Crash Course",
            language="English",
        )
        self.book2 = Book.objects.create(
            book_id=102,
            isbn="9780743273565",
            authors="F. Scott Fitzgerald",
            publication_year=1925,
            title="The Great Gatsby",
            language="English",
        )
        self.book3 = Book.objects.create(
            book_id=103,
            isbn="9780061120084",
            authors="Harper Lee",
            publication_year=1960,
            title="To Kill a Mockingbird",
            language="English",
        )
        self.book4 = Book.objects.create(
            book_id=104,
            isbn="9780439023528",
            authors="J.K. Rowling",
            publication_year=1997,
            title="Harry Potter and the Philosopher's Stone",
            language="English",
        )

        # Add Availability
        Availability.objects.create(book=self.book1, total_copies=5, available_copies=3)
        Availability.objects.create(book=self.book2, total_copies=2, available_copies=0)
        Availability.objects.create(book=self.book3, total_copies=1, available_copies=1)
        Availability.objects.create(book=self.book4, total_copies=3, available_copies=3)


class IndexViewTest(BaseViewTest):
    def setUp(self):
        return super().setUp()

    def test_index_view_get(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

        num_books = Book.objects.all().count()
        all_books_sum = Availability.objects.aggregate(Sum("total_copies", default=0))[
            "total_copies__sum"
        ]
        total_available_sum = Availability.objects.aggregate(
            Sum("available_copies", default=0)
        )["available_copies__sum"]

        self.assertEqual(response.context["num_books"], num_books)
        self.assertEqual(response.context["all_books"], all_books_sum)
        self.assertEqual(response.context["total_available"], total_available_sum)
        self.assertEqual(response.context["total_with_customer"], 0)  # No borrows
        self.assertEqual(
            response.context["average_lending"], "N/A"
        )  # No finished borrows

    def test_index_view_with_borrows(self):
        Borrows.objects.create(user=self.user1, book=self.book1)
        Borrows.objects.create(user=self.user2, book=self.book3)

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["total_with_customer"], 2)

    def test_index_view_with_average_lending_duration(self):
        Borrows.objects.create(
            user=self.user1,
            book=self.book1,
            created=timezone.now() - timedelta(days=5),
            returned=timezone.now() - timedelta(days=3),
        )
        Borrows.objects.create(
            user=self.user2,
            book=self.book2,
            created=timezone.now() - timedelta(days=10),
            returned=timezone.now() - timedelta(days=5),
        )
        Borrows.objects.create(
            user=self.user1,
            book=self.book3,
            created=timezone.now() - timedelta(days=1),
            returned=None,
        )

        response = self.client.get(reverse("index"))

        self.assertIn("days", response.context["average_lending"])
        self.assertIn("hours", response.context["average_lending"])
        self.assertIn("minutes", response.context["average_lending"])

    def test_index_view_post_not_allowed(self):
        response = self.client.post(reverse("index"))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed


class BookListViewTest(BaseViewTest):
    def test_book_list_view_no_search(self):
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "book_list.html")
        self.assertContains(response, "Python Crash Course")
        self.assertContains(response, "The Great Gatsby")

    def test_book_list_view_search_by_title_and(self):
        response = self.client.get(
            reverse("books"), {"title": "Python", "search_type": "1"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["book_list"],
            [self.book1],
            ordered=False,
        )
        self.assertContains(response, "Python Crash Course")
        self.assertNotContains(response, "The Great Gatsby")

    def test_book_list_view_search_by_author_or(self):
        response = self.client.get(
            reverse("books"), {"author": "Harper Lee", "search_type": "0"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["book_list"],
            [self.book3],
            ordered=False,
        )
        self.assertContains(response, "To Kill a Mockingbird")
        self.assertNotContains(response, "Python Crash Course")

    def test_book_list_view_search_by_title_and_author_and(self):
        response = self.client.get(
            reverse("books"),
            {"title": "Python", "author": "Harper Lee", "search_type": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["book_list"], [])

        response = self.client.get(
            reverse("books"),
            {"title": "Python", "author": "Eric Matthes", "search_type": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["book_list"], [self.book1], ordered=False
        )

    def test_book_list_view_search_by_title_and_author_or(self):

        response = self.client.get(
            reverse("books"),
            {"title": "Python", "author": "Harper Lee", "search_type": "0"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["book_list"],
            [self.book1, self.book3],
            ordered=False,
        )

    def test_book_list_view_wishlisted_and_borrowed_status_for_logged_in_user(self):
        Wishlist.objects.create(user=self.user1, book=self.book1)

        Borrows.objects.create(user=self.user1, book=self.book3)

        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)

        # Iterate through
        for book in response.context["book_list"]:
            if book.pk == self.book1.pk:
                self.assertTrue(book.is_wishlisted)
                self.assertFalse(book.is_borrowed)
            elif book.pk == self.book3.pk:
                self.assertFalse(book.is_wishlisted)
                self.assertTrue(book.is_borrowed)
            else:
                self.assertFalse(book.is_wishlisted)
                self.assertFalse(book.is_borrowed)

    def test_book_list_view_wishlisted_and_borrowed_status_for_anonymous_user(self):
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)

        for book in response.context["book_list"]:
            self.assertFalse(
                getattr(book, "is_wishlisted", False)
            )  # Use getattr to handle missing attributes gracefully
            self.assertFalse(getattr(book, "is_borrowed", False))


class BookSearchTest(BaseViewTest):
    def test_book_search_get_form_display(self):
        response = self.client.get(reverse("books_search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "book_search.html")

    def test_book_search_redirects_with_author_and_search_type(self):
        response = self.client.get(
            reverse("books_search"), {"author": "Rowling", "search_type": "1"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("books") + "?author=Rowling&title=&search_type=1"
        )

    def test_book_search_redirects_with_both_and_search_type(self):
        response = self.client.get(
            reverse("books_search"),
            {"title": "Gatsby", "author": "Fitzgerald", "search_type": "1"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("books") + "?author=Fitzgerald&title=Gatsby&search_type=1",
        )

    def test_book_search_post_not_allowed(self):
        response = self.client.post(reverse("books_search"))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
