from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from ..models import Cabinet

@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ['titre', 'ville', 'telephone', 'email', 'updated_at']
    search_fields = ['titre', 'ville', 'telephone', 'email']
    ordering = ['titre']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre',)
        }),
        ('Adresse', {
            'fields': ('rue', 'code_postal', 'ville')
        }),
        ('Contact', {
            'fields': ('telephone', 'email')
        }),
    )
    
    def has_add_permission(self, request):
        # Disable add if cabinet already exists
        return not Cabinet.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Disable delete permission
        return False
    
    def changelist_view(self, request, extra_context=None):
        # Redirect to change view if cabinet exists, otherwise to add view
        if Cabinet.objects.exists():
            cabinet = Cabinet.objects.first()
            return HttpResponseRedirect(f'../cabinet/{cabinet.id}/change/')
        else:
            return HttpResponseRedirect('../cabinet/add/')
    
    def response_add(self, request, obj, post_url_override=None):
        # After adding, redirect to change view
        return HttpResponseRedirect(f'../cabinet/{obj.id}/change/')
    
    def response_change(self, request, obj):
        # After changing, stay on the same page
        return HttpResponseRedirect('.')