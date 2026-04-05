from django.contrib.auth.models import User
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ExpenseTracker.settings')
django.setup()
try:
    u = User.objects.get(username='adityapandit705')
    print(f'User found: {u.username}, Active: {u.is_active}')
    u.is_active = True
    u.save()
    print('User activated successfully')
except User.DoesNotExist:
    print('User not found')
except Exception as e:
    print(f'Error: {e}')
