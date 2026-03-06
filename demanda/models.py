
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

class Area(models.Model):
    nomearea = models.CharField(max_length=100)

    def __str__(self):
        return self.nomearea


class Perfil(models.Model):
    tipo = models.CharField(max_length=50, choices=[('operador', 'Operador'), ('suporte', 'Suporte')])

    def __str__(self):
        return self.tipo


class Servico(models.Model):
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.descricao


class Urgencia(models.Model):
    URGENCIA_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    nivel = models.CharField(max_length=7, choices=URGENCIA_CHOICES)

    def __str__(self):
        return self.get_nivel_display()
 
    
    
    
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O usuário deve ter um email")
        usuario = self.model(email=self.normalize_email(email), **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')#
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)



class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  # Email como identificador único
    nome = models.CharField(max_length=100, unique=True)
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True)
    perfil = models.ForeignKey('Perfil', on_delete=models.SET_NULL, null=True, blank=True)
    area = models.ForeignKey('Area', on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'  # Define o email como campo de autenticação
    REQUIRED_FIELDS = ['nome', 'cpf']  # Campos obrigatórios ao criar superuser

    def __str__(self):
        return self.email

    

    
    
class Demanda(models.Model):
    STATUS_CHOICES = [
        ('Aberto', 'Aberto'),
        ('Fechado', 'Fechado'),
        ('Em Atendimento', 'Em Atendimento'),  # Adicionando opção correta
    ]
    
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    imagem = models.ImageField(upload_to='demandas/', null=True, blank=True)
    area = models.ForeignKey('Area', on_delete=models.CASCADE)

    # ERRADO (didatico):
    # status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Aberto')
    # status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Aberto')
    #
    # Declarar o mesmo campo 2x na classe gera sobrescrita silenciosa.
    # Isso confunde manutencao e pode gerar erro em migracao.
    #
    # CORRETO: manter apenas UMA declaracao do campo.
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Aberto')  # Aumentando max_length

    data_criacao = models.DateTimeField(auto_now_add=True)
    
    operador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='demandas_abertas')
   
    realizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='demandas_realizadas'
    )
   

    realizadoem = models.DateTimeField(null=True, blank=True)
    servico = models.ForeignKey('Servico', on_delete=models.CASCADE)
    urgencia = models.ForeignKey('Urgencia', on_delete=models.CASCADE)
    chave = models.CharField(max_length=20, unique=True, null=True, blank=True)
   


class Mensagem(models.Model):
    demanda = models.ForeignKey(Demanda, related_name='mensagens', on_delete=models.CASCADE)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensagem de {self.autor.get_full_name} em {self.data_envio}"







