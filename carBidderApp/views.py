from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from datetime import datetime, timedelta

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

    # Fetch the listings vehicles from the database
    listings = []
    if user_id:
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT listing_id, make, model, year_of_production, image_url, listing_status, listing_start_date
                    FROM LISTED_VEHICLES
                    WHERE seller_id = %s;
                """
                cursor.execute(query, [user_id])
                listings = cursor.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the error

    # Fetch the user's biddings from the database
    biddings = []
    
    if user_id:
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT b.bidding_id, b.listing_id, v.make, v.model, v.year_of_production, 
                           v.image_url, v.listing_status, b.bidding_amount, b.bidding_date, b.is_winner
                    FROM BIDDINGS b
                    INNER JOIN LISTED_VEHICLES v ON b.listing_id = v.listing_id
                    WHERE b.user_id = %s;
                """
                cursor.execute(query, [user_id])
                biddings = cursor.fetchall()
                # print(biddings)
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the error


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
        'listings': listings,
        'biddings': biddings,
        'current_page': 'profile',
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
        'current_page': 'violation_reports',
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
        'current_page': 'users',
    }

    return render(request, 'users.html', context)

def verify_vehicles(request):
    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    # Check if the request is a POST to update verification status
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        verification_action = request.POST.get('verification_action')

        new_status = None
        if verification_action == 'Verify':
            new_status = True
        elif verification_action == 'NotVerify':
            new_status = False
        # 'Not Started' will be represented by None, so no need for an explicit check

        # Update the database
        with connection.cursor() as cursor:
            cursor.execute("UPDATE LISTED_VEHICLES SET is_verified = %s WHERE vehicle_id = %s", [new_status, vehicle_id])

        # Redirect to the same page to prevent form resubmission on page refresh
        return redirect('verify_vehicles')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM LISTED_VEHICLES")
        vehicles = cursor.fetchall()

    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')

    context = {
        'vehicles': vehicles,
        'user_type': user_type,
        'user_name': user_name,
        'current_page': 'verify_vehicles',
    }

    return render(request, 'verify_vehicles.html', context)


def add_funds(request):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        amount = request.POST.get('amount')

        # Only proceed if the user is logged in as a normal user
        if not user_id or request.session.get('user_type') != 'NORMAL_USER':
            return HttpResponseRedirect('/')  # Redirect to home or show an error

        try:
            # Update the user's balance in the database
            with connection.cursor() as cursor:
                query = """
                    UPDATE USERS
                    SET balance = balance + %s
                    WHERE user_id = %s;
                """
                cursor.execute(query, (amount, user_id))
                connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the error (e.g., set an error message)

        # Optionally, update the session balance
        request.session['balance'] = str(float(request.session.get('balance', 0)) + float(amount))

        # Redirect to the profile page or show a success message
        return HttpResponseRedirect('/profile/')
    else:
        # Redirect or show an error if accessed directly
        return HttpResponseRedirect('/')
    

def orders(request):
    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    user_id = request.session.get('user_id', '')
    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')

    # Fetch orders from the database
    orders = []
    if user_id:
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT vo.order_id, vo.listing_id, lv.image_url, vo.order_price, 
                           vo.order_date, vo.is_shipped, vo.tracking_number, vo.is_paid
                    FROM VEHICLE_ORDERS vo
                    INNER JOIN LISTED_VEHICLES lv ON vo.listing_id = lv.listing_id
                    WHERE vo.buyer_id = %s;
                """
                cursor.execute(query, [user_id])
                orders = cursor.fetchall()
                print(orders)
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the error

    context = {'orders': orders,
                'user_type': user_type,
                'user_name': user_name,
                }
    return render(request, 'orders.html', context)

def weekly_reports(request):
    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')

    # Default start_date and end_date as None
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    report_data = None
    if start_date and end_date:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(order_price) AS TotalSaleAmount, COUNT(order_id) AS TotalNumberOfSales 
                FROM VEHICLE_ORDERS 
                WHERE order_date BETWEEN %s AND %s
            """, [start_date, end_date])
            
            report_data = cursor.fetchone()

    top_sellers = None 
    # Fetch top sellers data
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, user_name, seller_rating, num_of_seller_rating
            FROM USERS
            WHERE user_type = 'NORMAL_USER'
            ORDER BY seller_rating DESC, num_of_seller_rating DESC
            LIMIT 10
        """)
        top_sellers = cursor.fetchall()
    
    popular_vehicles = None 
    # Fetch top sellers data
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, user_name, seller_rating, num_of_seller_rating
            FROM USERS
            WHERE user_type = 'NORMAL_USER'
            ORDER BY seller_rating DESC, num_of_seller_rating DESC
            LIMIT 10
        """)
        popular_vehicles = cursor.fetchall()

    context = {
        'user_type': user_type,
        'user_name': user_name,
        'current_page': 'weekly_reports',
        'report_data': report_data,
        'start_date': start_date,
        'end_date': end_date,
        'top_sellers': top_sellers,
    }

    return render(request, 'weekly_reports.html', context)

    