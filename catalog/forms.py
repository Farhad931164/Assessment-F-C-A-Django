from django import forms


SEARCH_CHOICES = (
    (1, "AND"),
    (2, "OR"),
)


class BookSearch(forms.Form):
    title = forms.CharField(required=False)
    author = forms.CharField(required=False)
    search_type = forms.ChoiceField(choices=SEARCH_CHOICES, required=True)
