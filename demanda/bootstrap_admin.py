import os

from django.contrib.auth import get_user_model


def env_bool(key: str, default: bool = False) -> bool:
    return os.environ.get(key, str(default)).strip().lower() in ("1", "true", "yes", "on")


def ensure_admin_from_env(stdout_write=None) -> bool:
    """
    Cria (ou promove) um superusuario a partir de variaveis de ambiente.

    Retorna True se executou criacao/promocao, False caso tenha sido ignorado.
    """
    if not env_bool("AUTO_CREATE_ADMIN", False):
        if stdout_write:
            stdout_write("AUTO_CREATE_ADMIN desabilitado. Ignorando bootstrap de admin.")
        return False

    email = os.environ.get("ADMIN_EMAIL", "").strip()
    password = os.environ.get("ADMIN_PASSWORD", "").strip()
    nome = os.environ.get("ADMIN_NOME", "").strip()
    cpf = os.environ.get("ADMIN_CPF", "").strip()

    if not email or not password or not nome or not cpf:
        if stdout_write:
            stdout_write("Bootstrap admin ignorado: faltam ADMIN_EMAIL/ADMIN_PASSWORD/ADMIN_NOME/ADMIN_CPF.")
        return False

    User = get_user_model()
    user = User.objects.filter(email=email).first()

    if user:
        user.nome = nome
        user.cpf = cpf
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        if stdout_write:
            stdout_write("Usuario existente promovido para admin e senha atualizada.")
        return True

    User.objects.create_superuser(email=email, password=password, nome=nome, cpf=cpf)
    if stdout_write:
        stdout_write("Superusuario criado com sucesso.")
    return True
