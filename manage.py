#!/usr/bin/env python
"""Punto de entrada de administración de Django.

El literal `config.settings.local` es el mismo que declara `pyproject.toml`
para pytest. Es un valor compartido entre dos artefactos y el gate del paso 1
comprueba que ambos lo nombran igual.
"""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
