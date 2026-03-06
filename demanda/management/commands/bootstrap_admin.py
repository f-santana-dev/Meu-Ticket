from django.core.management.base import BaseCommand

from demanda.bootstrap_admin import ensure_admin_from_env


class Command(BaseCommand):
    help = "Cria um superusuario automaticamente (modo demo) a partir de variaveis de ambiente."

    def handle(self, *args, **options):
        executed = ensure_admin_from_env(stdout_write=self.stdout.write)
        if executed:
            self.stdout.write(self.style.SUCCESS("Bootstrap admin concluido."))
