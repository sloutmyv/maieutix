from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from authentication.models import SageFemmeUser


@admin.register(SageFemmeUser)
class SageFemmeUserAdmin(UserAdmin):
    """Administration des utilisateurs sages-femmes"""
    
    list_display = [
        'email',
        'is_active', 
        'is_staff',
        'must_change_password',
        'last_password_change',
        'date_joined'
    ]
    
    list_filter = [
        'is_active',
        'is_staff',
        'must_change_password',
        'date_joined'
    ]
    
    search_fields = ['email']
    
    ordering = ['email']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Mot de passe', {
            'fields': ('must_change_password', 'last_password_change')
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'must_change_password'),
        }),
    )
    
    readonly_fields = ['last_password_change', 'last_login', 'date_joined']
    
    def get_readonly_fields(self, request, obj=None):
        """Champs en lecture seule selon le contexte"""
        readonly = list(self.readonly_fields)
        if obj:  # Modification d'un utilisateur existant
            readonly.append('email')  # L'email ne peut pas être modifié
        return readonly