from django import forms
from django.contrib import admin

from .models import Movie


class MovieAdminForm(forms.ModelForm):
    """Muestra la descripción en un área de texto para poder leerla completa."""

    class Meta:
        model = Movie
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10, 'cols': 100}),
        }


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    form = MovieAdminForm
    list_display = ('id', 'title', 'year', 'genre', 'image')
    search_fields = ('title',)
