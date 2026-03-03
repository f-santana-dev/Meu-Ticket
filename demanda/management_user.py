

# def create_superuser(request):
#     try:
#         # Verifica se já existe um superusuário
#         if not User.objects.filter(is_superuser=True).exists():
#             call_command('createsuperuser', '--noinput', 'username=admin', 'email=bragasan34@gmail.com', 'password=101219')
#             return HttpResponse("Superusuário criado com sucesso!")
#         else:
#             return HttpResponse("Já existe um superusuário!")
#     except Exception as e:
#         return HttpResponse(f"Erro ao criar superusuário: {e}")


from django.http import HttpResponse
from django.core.management import call_command
from .models import Usuario

def create_superuser(request):
    try:
        # Verifica se já existe um superusuário
        if not Usuario.objects.filter(is_superuser=True).exists():
            # Chama o método create_superuser da sua classe UsuarioManager
            Usuario.objects.create_superuser(
                email='bragasan34@gmail.com', 
                password='101219', 
                nome='Francisco Santana',  # Aqui você pode colocar o nome do superusuário
                cpf='49322893249'  # Coloque o CPF do superusuário
            )
            return HttpResponse("Superusuário criado com sucesso!")
        else:
            return HttpResponse("Já existe um superusuário!")
    except Exception as e:
        return HttpResponse(f"Erro ao criar superusuário: {e}")