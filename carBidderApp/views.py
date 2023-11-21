from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.hashers import make_password
import uuid 

cur_user = {}

def testmysql(request):

    # user_type = request.session.get('user_type', '')
    # user_name = request.session.get('user_name', '')
    cur_user = request.session.get('cur_user', '')
    # context = {
    #     'user_type': user_type,
    #     'user_name': user_name,
    # }
    return render(request, 'home.html', cur_user)

def register(request):
    if request.method == "POST":
        try:
            # Get data from POST request
            user_type = request.POST.get('user_type', '')
            user_name = request.POST.get('user_name', '')
            email = request.POST.get('email', '')

            # Insert data into the database
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO USERS (user_type, user_name, email)
                    VALUES (%s, %s, %s);
                """
                cursor.execute(query, (user_type, user_name, email))
                connection.commit()
                return redirect('home')
        except Exception as e:
            # Handle any errors that occur during the process
            print(f"An error occurred: {e}")
            # Optionally, add error handling logic here (e.g., set an error message, rollback transaction)

    # Render the registration form for both GET and POST requests
    return render(request, 'register.html')

def login(request):
    if request.method == "POST":
        try:
            # Get data from POST request
            user_email = request.POST.get('email', '')

            # Query the database
            with connection.cursor() as cursor:
                query = """
                    SELECT * 
                    FROM USERS
                    WHERE email = %s;
                """
                cursor.execute(query, [user_email])  # Pass parameters as a list
                t = cursor.fetchall()
                if not t:
                    return render(request, 'error.html')
                else:
                    # return render(request, "home.html", context)
                    cur_user = t
                    print(cur_user)
                    user_data = t[0]
                    user_type = user_data[1]
                    user_name = user_data[2]
                    email = user_data[3]

                    cur_user = {
                        'user_type': user_type,
                        'user_name': user_name,
                        'email': email,

                    }
                    request.session['cur_user'] = cur_user
                    return redirect('home')
        except Exception as e:
            # Handle any errors that occur during the process
            print(f"An error occurred: {e}")
            # Optionally, add error handling logic here

    # Render the login form for GET requests
    return render(request, 'login.html')


def logout(request):
    request.session.flush()
    return redirect('home')

def profile(request):

    # context = {
    #     'user_type': "user_type",
    #     'user_name': "user_name",
    # }
    cur_user = request.session.get('cur_user', '')
    return render(request, 'profile.html', cur_user)