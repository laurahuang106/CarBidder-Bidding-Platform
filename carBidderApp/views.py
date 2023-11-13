from django.shortcuts import render
from django.db import connection
# from .models import Employee

# Create your views here.
def testmysql(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            select user_name
            from users;
        """)

        rows = cursor.fetchall()

    context = {
        'user_name': rows,
    }
    return render(request, 'home.html', context)
