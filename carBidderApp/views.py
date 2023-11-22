from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.hashers import make_password
import uuid 

cur_user = {}

def home(request):

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

def update_session(request, email):
    """
    Update the session with the user's data based on the provided email.
    """
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT * 
                FROM USERS
                WHERE email = %s;
            """
            cursor.execute(query, [email])
            user_data = cursor.fetchone()

            if user_data:
                # Extracting user data and updating the session
                request.session['user_id'] = user_data[0]
                request.session['user_type'] = user_data[1]
                request.session['user_name'] = user_data[2]
                request.session['email'] = user_data[3]
                request.session['balance'] = str(user_data[4])  # Convert Decimal to string
                request.session['seller_rating'] = str(user_data[5])  # Convert Decimal to string
                request.session['buyer_rating'] = str(user_data[6])  # Convert Decimal to string
                request.session['num_of_seller_rating'] = user_data[7]
                request.session['num_of_buyer_rating'] = user_data[8]
                request.session['is_allow_chat'] = user_data[9]
                request.session['is_allow_list'] = user_data[10]
            else:
                # Handle case where user data is not found
                # You can redirect to an error page or set an error message
                pass

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, handle the exception (e.g., set an error message, redirect)


def login(request):
    if request.method == "POST":
        try:
            user_email = request.POST.get('email', '')
            update_session(request, user_email)
            return redirect('home')
        except Exception as e:
            print(f"An error occurred: {e}")

    return render(request, 'login.html')



def logout(request):
    request.session.flush()
    return redirect('home')


def profile(request):
    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)
        
    # Fetching data from the session
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

    # Creating the context dictionary
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


def report(request):
    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM VIOLATION_REPORTS")
        violation_reports = cursor.fetchall()

    if request.method == 'POST':
        report_id_to_delete = request.POST.get('report_id_to_delete')
        if report_id_to_delete:
            # Delete the report with the specified report_id using a cursor
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM VIOLATION_REPORTS WHERE report_id = %s", [report_id_to_delete])

            # Redirect back to the report page after deleting
            return redirect('report')
    
    # Add violation reports to the context
    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')
    context = {
        'violation_reports': violation_reports,
        'user_type': user_type,
        'user_name': user_name,

    }

    return render(request, 'report.html', context)


def users(request):
    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM USERS")
        users = cursor.fetchall()
    
    if request.method == 'POST':
        user_id_to_toggle_mute = request.POST.get('user_id_to_toggle_mute')
        if user_id_to_toggle_mute:
            with connection.cursor() as cursor:
                # Check if the user is currently muted or not
                cursor.execute("SELECT is_allowed_chat FROM USERS WHERE user_id = %s", [user_id_to_toggle_mute])
                is_muted = cursor.fetchone()[0]
                
                # Toggle mute status
                new_status = not is_muted
                cursor.execute("UPDATE USERS SET is_allowed_chat = %s WHERE user_id = %s", [new_status, user_id_to_toggle_mute])
            
            return redirect('users') 
    
    if request.method == 'POST':
        user_id_to_toggle_list = request.POST.get('user_id_to_toggle_list')
        if user_id_to_toggle_list:
            with connection.cursor() as cursor:
                # Check the current listing permission of the user
                cursor.execute("SELECT is_allow_list FROM USERS WHERE user_id = %s", [user_id_to_toggle_list])
                can_list = cursor.fetchone()[0]

                # Toggle the permission
                new_list_status = not can_list
                cursor.execute("UPDATE USERS SET is_allow_list = %s WHERE user_id = %s", [new_list_status, user_id_to_toggle_list])

            return redirect('users')
    
    # Add violation reports to the context
    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')
    context = {
        'users': users,
        'user_type': user_type,
        'user_name': user_name,
    }

    return render(request, 'users.html', context)