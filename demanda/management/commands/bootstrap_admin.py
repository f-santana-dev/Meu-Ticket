import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


def env_bool(key: str, default: bool = False) -> bool:
    return os.environ.get(key, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Command(BaseCommand):
    help = "Cria um superusuario automaticamente (modo demo) a partir de variaveis de ambiente."

    def handle(self, *args, **options):
        if not env_bool("AUTO_CREATE_ADMIN", False):
            self.stdout.write("AUTO_CREATE_ADMIN desabilitado. Nenhuma criacao automatica executada.")
            return

        email = os.environ.get("ADMIN_EMAIL", "").strip()
        password = os.environ.get("ADMIN_PASSWORD", "").strip()
        nome = os.environ.get("ADMIN_NOME", "").strip()
        cpf = os.environ.get("ADMIN_CPF", "").strip()

        if not email or not password or not nome or not cpf:
            self.stdout.write(
                "Variaveis incompletas. Necessarias: ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NOME, ADMIN_CPF."
            )
            return

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            self.stdout.write("Admin ja existe. Criacao automatica ignorada.")
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            nome=nome,
            cpf=cpf,
        )

        self.stdout.write(self.style.SUCCESS("Superusuario criado com sucesso."))

