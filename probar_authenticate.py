#!/usr/bin/env python
"""
Script para probar la autenticación de Django con credenciales dadas.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_prestamos.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model

def main():
    User = get_user_model()
    users = list(User.objects.values_list('username', flat=True))
    print("Usuarios en BD:", users)

    for username, password in [
        ('jhamir14', 'jhamirquispe'),
        ('jhamir14', 'admin123'),
        ('admin', 'admin123'),
    ]:
        user = authenticate(username=username, password=password)
        print(f"authenticate({username}, {password}):", bool(user))

if __name__ == '__main__':
    main()