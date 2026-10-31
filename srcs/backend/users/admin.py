from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'type_of_user')
    list_filter = ('type_of_user',)
    search_fields = ('username', 'email')
    filter_horizontal = ('tags',)     # scegli i tag dell'utente con il selettore
