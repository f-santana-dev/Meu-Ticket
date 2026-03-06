from django.apps import AppConfig


class DemandaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'demanda'

    def ready(self):
        # Executa automaticamente apos `migrate` (Render free), se AUTO_CREATE_ADMIN=True.
        from django.db.models.signals import post_migrate

        def _bootstrap_admin(sender, **kwargs):
            from demanda.bootstrap_admin import ensure_admin_from_env

            ensure_admin_from_env()

        post_migrate.connect(_bootstrap_admin, sender=self, dispatch_uid="demanda_bootstrap_admin")
