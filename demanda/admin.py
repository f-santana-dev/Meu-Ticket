from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Area, Demanda, Perfil, Servico, Urgencia, Usuario
from .forms import UsuarioAdminChangeForm, UsuarioAdminCreationForm


admin.site.register(Area)
admin.site.register(Demanda)
admin.site.register(Perfil)
admin.site.register(Servico)
admin.site.register(Urgencia)


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    
    # IMPORTANTE (didatico):
    # Como o model Usuario e customizado (usa email como login), precisamos dizer ao admin
    # quais formularios usar. Sem isso, o Django tenta usar os forms do User padrao (username),
    # o que costuma causar erro 500 na tela /admin/demanda/usuario/.
    add_form = UsuarioAdminCreationForm
    form = UsuarioAdminChangeForm
    model = Usuario

   
    list_display = ("email", "nome", "cpf", "perfil", "area", "is_staff", "is_active")
    search_fields = ("email", "nome", "cpf")
    list_filter = ("is_staff", "is_active", "perfil", "area")
    ordering = ("email",)

    fieldsets = (
        ("Acesso", {"fields": ("email", "password")}),
        ("Dados pessoais", {"fields": ("nome", "cpf", "perfil", "area")}),
        ("Permissoes", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Datas", {"fields": ("last_login", "data_criacao")}),
    )

    add_fieldsets = (
        (
            "Criacao de usuario",
            {
                "classes": ("wide",),
                "fields": ("email", "nome", "cpf", "perfil", "area", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )

    readonly_fields = ("data_criacao", "last_login")
    filter_horizontal = ("groups", "user_permissions")
