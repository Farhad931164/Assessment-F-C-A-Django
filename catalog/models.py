import datetime as dt
from django.core import exceptions
from django.core import validators
from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    book_id = models.PositiveIntegerField(primary_key=True)
    isbn = models.CharField(max_length=13, unique=True)
    authors = models.CharField(max_length=255)
    publication_year = models.IntegerField(
        validators=[
            validators.MinValueValidator(-1000),
            validators.MaxValueValidator(dt.datetime.now().year + 1),
        ]
    )
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.title} by {self.authors} ({self.publication_year})"

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["title"]


#  you can add book availability to book table but this is more normalized and also it is future proof
#  so if you want to add shelf number, row number etc later
class Availability(models.Model):
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,  # Delete cascade
        primary_key=True,
        related_name="availability",  # book.availability.available_copies
    )
    total_copies = models.IntegerField(default=0)
    available_copies = models.IntegerField(default=0)

    def clean(self):
        if self.total_copies < self.available_copies:
            raise exceptions.ValidationError(
                "Number of available books cannot be more than total copies."
            )

    def __str__(self):
        return f"Availability for '{self.book.title}': {self.available_copies}/{self.total_copies} available"

    class Meta:
        verbose_name = "Book Availability"
        verbose_name_plural = "Book Availabilities"


class Wishlist(models.Model):
    pk = models.CompositePrimaryKey("user_id", "book_id")  # this is new in Django 5
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Delet Cascade
        related_name="wishlist_items",  # user.wishlist_items.all()
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,  # Cascade if a book is deleted from table
        related_name="wishlisted_by",  # book.wishlisted_by.all()
    )

    class Meta:
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"

    def __str__(self):
        return f"{self.user.username}'s wishlist: {self.book.title}"


class AmazonLink(models.Model):
    pk = models.CompositePrimaryKey("book_id", "url")  # this is new in Django 5

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,  # Delete cascade
        related_name="amazon_links",  #  book.amazon_links.all
    )
    url = models.URLField(max_length=200)

    class Meta:
        verbose_name = "Book link On Amazon"
        verbose_name_plural = "Book Links on Amazon"

    def __str__(self):
        return f"{self.book.title} - {self.url} Amazon Link"
