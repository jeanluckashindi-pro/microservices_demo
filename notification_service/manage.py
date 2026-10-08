#!/usr/bin/env python
"""
NOTIFICATION SERVICE - Point d'entrée Django.
"""
import os
import sys


def main():
    """Lance les commandes Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Vérifiez que Django est installé "
            "et que DJANGO_SETTINGS_MODULE est correctement configuré."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
