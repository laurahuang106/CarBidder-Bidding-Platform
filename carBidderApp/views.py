from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.hashers import make_password
import uuid 

cur_user = {}

def home(request):
    # with connection.cursor() as cursor:
    #     cursor.execute("""
    #         select VIN
    #         from LISTED_VEHICLES
    #     """)

    #     rows = cursor.fetchall()

    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')

    context = {
        'user_type': user_type,
        'user_name': user_name,
    }
    return render(request, 'home.html', context)

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
                    user_id = user_data[0]
                    user_type = user_data[1]
                    user_name = user_data[2]
                    email = user_data[3]
                    balance = user_data[4]
                    seller_rating = user_data[5]
                    buyer_rating = user_data[6]
                    num_of_seller_rating = user_data[7]
                    num_of_buyer_rating = user_data[8]
                    is_allow_chat = user_data[9]
                    is_allow_list = user_data[10]

                    # # Assigning values to the session 
                    # request.session['user_id'] = user_id
                    # request.session['user_type'] = user_type
                    # request.session['user_name'] = user_name
                    # request.session['email'] = email
                    # request.session['balance'] = balance
                    # request.session['seller_rating'] = seller_rating
                    # request.session['buyer_rating'] = buyer_rating
                    # request.session['num_of_seller_rating'] = num_of_seller_rating
                    # request.session['num_of_buyer_rating'] = num_of_buyer_rating
                    # request.session['is_allow_chat'] = is_allow_chat
                    # request.session['is_allow_list'] = is_allow_list

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
    user_id = request.session.get('user_id', '')
    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')
    email = request.session.get('email', '')
    balance = request.session.get('balance', '')
    seller_rating = request.session.get('seller_rating', '')
    buyer_rating = request.session.get('buyer_rating', '')
    num_of_seller_rating = request.session.get('num_of_seller_rating', '')
    num_of_buyer_rating = request.session.get('num_of_buyer_rating', '')
    is_allow_chat = request.session.get('is_allow_chat', '')
    is_allow_list = request.session.get('is_allow_list', '')

    context = {
        'user_id': user_id,
        'user_type': user_type,
        'user_name': user_name,
        'email': email,
        'balance': balance,
        'seller_rating': seller_rating,
        'buyer_rating': buyer_rating,
        'num_of_seller_rating': num_of_seller_rating,
        'num_of_buyer_rating': num_of_buyer_rating,
        'is_allow_chat': is_allow_chat,
        'is_allow_list': is_allow_list,
    }
    return render(request, 'profile.html', context)