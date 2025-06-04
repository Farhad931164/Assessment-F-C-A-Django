#!/bin/bash
read -p "Press Enter to run Django makemigrations"
uv run python manage.py makemigrations

read -p "Press Enter to run Django migrate"
uv run python python manage.py migrate

read -p "Press Enter to run Django server"
uv run python python manage.py runserver
