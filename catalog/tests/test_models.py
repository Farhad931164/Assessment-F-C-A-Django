from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from catalog.models import Book, Wishlist, Borrows, AmazonLink
import datetime as dt

class BookModelTest(TestCase):
    def setUp(self):
        # Create a sample book to be used by multiple tests
        self.book1 = Book.objects.create(
            book_id=1,
            isbn="9780321765723",
            authors="Eric Matthes",
            publication_year=2019,
            title="Python Crash Course",
            language="English"
        )
        self.book2 = Book.objects.create(
            book_id=2,
            isbn="9780743273565",
            authors="F. Scott Fitzgerald",
            publication_year=1925,
            title="The Great Gatsby",
            language="English"
        )

    def test_book_creation(self):
        """
        Test that a Book instance can be created and saved successfully.
        """
        book = Book.objects.get(book_id=self.book1.book_id)
        self.assertEqual(book.isbn, "9780321765723")
        self.assertEqual(book.authors, "Eric Matthes")
        self.assertEqual(book.publication_year, 2019)
        self.assertEqual(book.title, "Python Crash Course")
        self.assertEqual(book.language, "English")

    def test_book_str_representation(self):
        """
        Test the __str__ method returns the expected string.
        """
        expected_str = "Python Crash Course by Eric Matthes (2019), Book ID: 1"
        self.assertEqual(str(self.book1), expected_str)

    def test_isbn_unique_constraint(self):
        """
        Test that two books cannot have the same ISBN.
        """
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                book_id=3,
                isbn="9780321765723",  # Duplicate ISBN
                authors="Another Author",
                publication_year=2020,
                title="Another Book",
                language="English"
            )

    def test_publication_year_min_validator(self):
        """
        Test that publication_year cannot be less than -1000.
        """
        book = Book(
            book_id=4,
            isbn="9781234567890",
            authors="Test Author",
            publication_year=-1001,  # Invalid year
            title="Ancient History",
            language="Latin"
        )
        with self.assertRaises(ValidationError):
            book.full_clean() # full_clean() runs all model validations

    def test_publication_year_max_validator(self):
        """
        Test that publication_year cannot be greater than current year + 1.
        """
        future_year = dt.datetime.now().year + 2
        book = Book(
            book_id=5,
            isbn="9780987654321",
            authors="Future Author",
            publication_year=future_year,  # Invalid year
            title="Future Science",
            language="English"
        )
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_publication_year_valid(self):
        """
        Test that a valid publication year is accepted.
        """
        current_year = dt.datetime.now().year
        book = Book.objects.create(
            book_id=6,
            isbn="9781122334455",
            authors="Valid Author",
            publication_year=current_year,
            title="Current Events",
            language="English"
        )
        self.assertEqual(book.publication_year, current_year)
        # No exception should be raised, confirming valid year is accepted
        book.full_clean()

    def test_meta_options(self):
        """
        Test the Meta options (verbose_name, verbose_name_plural, ordering).
        """
        self.assertEqual(self.book1._meta.verbose_name, "Book")
        self.assertEqual(self.book1._meta.verbose_name_plural, "Books")
        # Ordering is checked implicitly by Django's ORM, but we can verify the option
        self.assertEqual(self.book1._meta.ordering, ["title"])

    def test_book_update(self):
        """
        Test updating an existing book's details.
        """
        self.book1.title = "Python Crash Course, 2nd Edition"
        self.book1.publication_year = 2020
        self.book1.save()
        updated_book = Book.objects.get(book_id=self.book1.book_id)
        self.assertEqual(updated_book.title, "Python Crash Course, 2nd Edition")
        self.assertEqual(updated_book.publication_year, 2020)

    def test_book_deletion(self):
        """
        Test deleting a book from the database.
        """
        initial_count = Book.objects.count()
        self.book2.delete()
        self.assertEqual(Book.objects.count(), initial_count - 1)
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(book_id=self.book2.book_id)