from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Area, Demanda, Usuario,Perfil , Urgencia,Servico#Status

admin.site.register(Area)
#admin.site.register(Status)
admin.site.register(Demanda)
admin.site.register(Perfil)
admin.site.register(Servico)
admin.site.register(Urgencia)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome', 'cpf', 'is_staff', 'is_active')  # Campos a serem exibidos na listagem
    search_fields = ('email', 'nome')  # Campos pesquisáveis
    list_filter = ('is_staff', 'is_active')  # Filtros disponíveis
    ordering = ('email',)  # Ordenação padrão
    
    