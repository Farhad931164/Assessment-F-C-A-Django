# The library django application - FCA assessment

This is a simple library web application built with Django. Having previously used FastAPI for a similar assessment at FCA, I chose Django to not to repeat the same thing.


## Table of Contents

- [The library django application - FCA assessment](#the-library-django-application---fca-assessment)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Tests](#tests)


## Features

- Any user can see a list of all books
- Any user can search through list of all books
  - search by title
  - search by author
- A library user can add a book to wishlist
- A library user can remove a book from wishlist
- A librarian can return a book to library
- A librarian can lend book
- A librarian can see the report of books 

## Tech Stack

- Django
- Pandas
- Sqlite

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Farhad931164/Assessment-F-C-A-Django.git

    cd Assessment-F-C-A-Django
    ```

2.  **Create a virtual environment:**

    ```bash
    uv sync
    ```


3.  **Run the development server:**

    ```bash
    uv run python manage.py runserver
    ```

## Usage

Access the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/) or [http://localhost:8000/](http://localhost:8000/).
The standard django admin panel login comes up. You have two user available to login.

  1. username: `user` and password `user`
  2. username: `admin` and password `admin`

Once you log in, you'll be taken directly to the main page of the library application. While it's functional enough to explore, please understand that it's a work in progress and I ran out of time to fully complete it. Regarding the API, it generally follows standard practices, but there are a few instances where I had to make compromises, especially since standard HTML forms don't directly support the DELETE method on form submit.

## Tests
Unit tests have been implemented here for demonstration. Since this is not a production codebase, the testing primarily serves to showcase how unit testing can be achieved with Django's standard libraries. To execute these tests, use the following command:

    ```bash
    uv run python manage.py runserver
    ```