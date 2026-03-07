from django import forms
from .models import Demanda, Servico, Usuario, Urgencia
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import template


class UsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['email', 'nome', 'cpf', 'perfil', 'area']  # Não precisa adicionar os campos de senha aqui

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  # Utilize 'password1' ao invés de 'password'
        if commit:
            user.save()
        return user


class UsuarioAdminCreationForm(UserCreationForm):
    """
    Form usado SOMENTE no Django Admin para criar o Usuario customizado.

    Importante: o UserAdmin padrao espera campos do User default (ex: username).
    Como nosso model usa email, precisamos de um form explicitamente baseado em Usuario,
    com os mesmos campos declarados em UsuarioAdmin.add_fieldsets.
    """

    class Meta:
        model = Usuario
        fields = ["email", "nome", "cpf", "perfil", "area", "is_staff", "is_active"]


class UsuarioAdminChangeForm(UserChangeForm):
    """
    Form usado SOMENTE no Django Admin para editar o Usuario customizado.

    Sem isso, a tela /admin/demanda/usuario/ pode quebrar ao tentar renderizar campos
    que nao existem no User default (ex: username) ou ao usar forms incorretos.
    """

    class Meta:
        model = Usuario
        fields = [
            "email",
            "password",
            "nome",
            "cpf",
            "perfil",
            "area",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "last_login",
            "data_criacao",
        ]


register = template.Library()
@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class + (" is-invalid" if field.errors else "")})






class Nova_DemandaForm(forms.ModelForm):
    class Meta:
        model = Demanda
        fields = ['titulo', 'descricao', 'imagem', 'urgencia', 'servico']

        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da demanda'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    # Definindo urgencia e servico como obrigatórios
    urgencia = forms.ModelChoiceField(
        queryset=Urgencia.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Selecione a Prioridade",
        required=True,
        error_messages={'required': 'Por favor, selecione uma prioridade.'}  # Mensagem de erro personalizada
    )
    
    servico = forms.ModelChoiceField(
        queryset=Servico.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Selecione um Serviço",
        required=True,
        error_messages={'required': 'Por favor, selecione um serviço.'}  # Mensagem de erro personalizada
    )

    # Definindo 'titulo' e 'descricao' como obrigatórios
    titulo = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da demanda'}),
        error_messages={'required': 'O título é obrigatório.'}  # Mensagem de erro personalizada
    )

    descricao = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição'}),
        error_messages={'required': 'A descrição é obrigatória.'}  # Mensagem de erro personalizada
    )

    # Campo 'imagem' não é obrigatório
    imagem = forms.ImageField(
        required=False,  # Torna o campo não obrigatório
    )
    
    
