from gettext import translation
import random
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, timedelta
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db import IntegrityError
from datetime import datetime
from django.contrib import messages
import time
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('MY_API_KEY')

cur_user = {}


def home(request):
    handle_comment_submission(request)

    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')
    is_seller = request.session.get('is_seller', '')

    context = {
        'user_type': user_type,
        'user_name': user_name,
        'is_seller': is_seller,
    }
    return render(request, 'home.html', context)


def handle_comment_submission(request):
    if request.method == 'POST' and 'comment' in request.POST:
        print('here1')
        if 'user_id' in request.session:
            user_id = request.session.get('user_id')
            report_content = request.POST.get('comment')
            print('here2')
            print(user_id)
            print(report_content)
            try:
                with connection.cursor() as cursor:
                    query = """
                        INSERT INTO VIOLATION_REPORTS (user_id, report_content)
                        VALUES (%s, %s);
                    """
                    cursor.execute(query, (user_id, report_content))
                    connection.commit()
                messages.success(
                    request, 'Your comment has been successfully submitted.')
            except Exception as e:
                print(f"An error occurred: {e}")
                messages.error(
                    request, 'An error occurred while submitting your comment.')

            return redirect('home')


def is_email_valid(email):
    with connection.cursor() as cursor:
        cursor.execute("SELECT email FROM USERS WHERE email = %s", [email])
        return cursor.fetchone() is not None


def register(request):
    message = None

    if request.method == "POST":
        user_type = request.POST.get('user_type', '')
        user_name = request.POST.get('user_name', '')
        email = request.POST.get('email', '')

        if not is_email_valid(email):  # Check if the email is not already in use
            try:
                with connection.cursor() as cursor:
                    query = """
                        INSERT INTO USERS (user_type, user_name, email)
                        VALUES (%s, %s, %s);
                    """
                    cursor.execute(query, (user_type, user_name, email))
                    connection.commit()

                message = "Registration successful! "
            except Exception as e:
                print(f"An error occurred: {e}")
                message = "An error occurred during registration. Please try again."
        else:
            message = "Email already in use. Please choose a different email."

    return render(request, 'register.html', {'message': message, 'current_page': 'register'})


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
                request.session['balance'] = str(
                    user_data[4])  # Convert Decimal to string
                request.session['seller_rating'] = str(
                    user_data[5])  # Convert Decimal to string
                request.session['buyer_rating'] = str(
                    user_data[6])  # Convert Decimal to string
                request.session['num_of_seller_rating'] = user_data[7]
                request.session['num_of_buyer_rating'] = user_data[8]
                request.session['is_allow_chat'] = user_data[9]
                request.session['is_allow_list'] = user_data[10]
                is_seller(request, user_data[0])
            else:
                # Handle case where user data is not found
                # You can redirect to an error page or set an error message
                pass

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, handle the exception (e.g., set an error message, redirect)


def is_seller(request, user_id):
    is_seller = False
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM LISTED_VEHICLES
            WHERE seller_id = %s
        """, [user_id])
        count = cursor.fetchone()[0]
        if count > 0:
            is_seller = True

    request.session['is_seller'] = is_seller


def login(request):
    error_message = None  # Variable to hold the error message

    if request.method == "POST":
        user_email = request.POST.get('email', '')

        if user_email:
            try:
                if is_email_valid(user_email):
                    update_session(request, user_email)
                    return redirect('search_car')
                else:
                    error_message = "Email does not exist. Please try again or"
            except Exception as e:
                print(f"An error occurred: {e}")
                error_message = "An error occurred during login. Please try again."
        else:
            error_message = "Please enter an email address."

    return render(request, 'login.html', {'error_message': error_message, 'current_page': 'login'})


def is_email_valid(email):
    with connection.cursor() as cursor:
        cursor.execute("SELECT email FROM USERS WHERE email = %s", [email])
        return cursor.fetchone() is not None


def logout(request):
    request.session.flush()
    return redirect('home')


def profile(request):
    # enable write commnets
    handle_comment_submission(request)

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
    is_seller = request.session.get('is_seller', '')

    listings = []
    if user_id:
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT lv.listing_id, lv.make, lv.model, lv.year_of_production, 
                        lv.image_url, lv.listing_status, lv.listing_start_date, 
                        vo.order_id, vo.is_paid, vo.is_shipped, lv.is_verified
                    FROM LISTED_VEHICLES lv
                    LEFT JOIN VEHICLE_ORDERS vo ON lv.listing_id = vo.listing_id
                    WHERE lv.seller_id = %s;
                """
                cursor.execute(query, [user_id])
                for row in cursor.fetchall():
                    # Check if order is paid and shipped
                    rate_buyer_link = None
                    if row[7] is not None and row[8] == b'\x01' and row[9] == b'\x01':
                        rate_buyer_link = f"seller_rate_buyer/{row[7]}/"
                    listings.append(row + (rate_buyer_link,))

        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the error
    print(listings)

    # Fetch the user's biddings from the database
    biddings = []

    if user_id:
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT b.bidding_id, b.listing_id, v.make, v.model, v.year_of_production, 
                        v.image_url, v.listing_status, b.bidding_amount, b.bidding_date, b.is_winner,
                        s.user_id, s.user_name
                    FROM BIDDINGS b
                    INNER JOIN LISTED_VEHICLES v ON b.listing_id = v.listing_id
                    INNER JOIN USERS s ON v.seller_id = s.user_id
                    WHERE b.user_id = %s;
                """
                cursor.execute(query, [user_id])
                biddings = cursor.fetchall()
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
        'is_seller': is_seller,
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
                cursor.execute("DELETE FROM VIOLATION_REPORTS WHERE report_id = %s", [
                               report_id_to_delete])

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
                cursor.execute("SELECT is_allowed_chat FROM USERS WHERE user_id = %s", [
                               user_id_to_toggle_mute])
                is_muted = cursor.fetchone()[0]

                # Toggle mute status
                new_status = not is_muted
                cursor.execute("UPDATE USERS SET is_allowed_chat = %s WHERE user_id = %s", [
                               new_status, user_id_to_toggle_mute])

            return redirect('users')

    if request.method == 'POST':
        user_id_to_toggle_list = request.POST.get('user_id_to_toggle_list')
        if user_id_to_toggle_list:
            with connection.cursor() as cursor:
                # Check the current listing permission of the user
                cursor.execute("SELECT is_allow_list FROM USERS WHERE user_id = %s", [
                               user_id_to_toggle_list])
                can_list = cursor.fetchone()[0]

                # Toggle the permission
                new_list_status = not can_list
                cursor.execute("UPDATE USERS SET is_allow_list = %s WHERE user_id = %s", [
                               new_list_status, user_id_to_toggle_list])

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
        listing_id = request.POST.get('listing_id')
        verification_action = request.POST.get('verification_action')

        new_status = None
        listing_status = None
        if verification_action == 'Verify':
            new_status = True
            listing_status = True
        elif verification_action == 'NotVerify':
            new_status = False
            listing_status = False
        # 'Not Started' will be represented by None, so no need for an explicit check

        # # Update the database
        # with connection.cursor() as cursor:
        #     cursor.execute("UPDATE LISTED_VEHICLES SET is_verified = %s WHERE listing_id = %s", [
        #                    new_status, listing_id])
        with connection.cursor() as cursor:
            # The following UPDATE statement sets the is_verified and listing_status columns
            cursor.execute("""
                UPDATE LISTED_VEHICLES 
                SET is_verified = %s, listing_status = %s 
                WHERE listing_id = %s
            """, [new_status, listing_status, listing_id])
            connection.commit()

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
            # Redirect to home or show an error
            return HttpResponseRedirect('/')

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
        request.session['balance'] = str(
            float(request.session.get('balance', 0)) + float(amount))

        # Redirect to the profile page or show a success message
        return HttpResponseRedirect('/profile/')
    else:
        # Redirect or show an error if accessed directly
        return HttpResponseRedirect('/')


def orders(request):
    # enable write commnets
    handle_comment_submission(request)

    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    user_id = request.session.get('user_id', '')
    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')
    is_seller = request.session.get('is_seller', '')

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
                rows = cursor.fetchall()
                for row in rows:
                    # Check if both is_shipped and is_paid are True
                    is_shipped_and_paid = row[5] == b'\x01' and row[7] == b'\x01'
                    # Check if is_shipped is True
                    is_shipped = row[5] == b'\x01'
                    # Check if is_paid is True
                    is_paid = row[7] == b'\x01'

                    # Append these three boolean values to the row
                    orders.append(
                        row + (is_shipped_and_paid, is_shipped, is_paid))

                print(orders)

        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the error

    context = {'orders': orders,
               'user_type': user_type,
               'user_name': user_name,
               'is_seller': is_seller,
               'current_page': 'orders',
               }
    return render(request, 'orders.html', context)


def weekly_reports(request):
    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')

    start_date = None
    end_date = None
    vehicle_start_date = None
    vehicle_end_date = None
    if 'start_date' in request.POST:
        # Default start_date and end_date as None
        request.session['start_date'] = request.POST.get('start_date')
        request.session['end_date'] = request.POST.get('end_date')

    elif 'vehicle_start_date' in request.POST:
        request.session['vehicle_start_date'] = request.POST.get(
            'vehicle_start_date')
        request.session['vehicle_end_date'] = request.POST.get(
            'vehicle_end_date')

    # Retrieve from session if available
    start_date = request.session.get('start_date', '')
    end_date = request.session.get('end_date', '')
    vehicle_start_date = request.session.get('vehicle_start_date', '')
    vehicle_end_date = request.session.get('vehicle_end_date', '')

    # get sales report
    report_data = None
    if start_date and end_date:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(order_price) AS TotalSaleAmount, COUNT(order_id) AS TotalNumberOfSales 
                FROM VEHICLE_ORDERS 
                WHERE order_date BETWEEN %s AND %s
            """, [start_date, end_date])

            report_data = cursor.fetchone()

    popular_vehicles = None
    if vehicle_start_date and vehicle_end_date:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    listing_id, 
                    make, 
                    model, 
                    year_of_production, 
                    number_of_bids
                FROM (
                    SELECT 
                        LV.listing_id AS listing_id, 
                        LV.make AS make, 
                        LV.model AS model, 
                        LV.year_of_production AS year_of_production, 
                        COUNT(*) AS number_of_bids,
                        DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS bid_rank
                    FROM 
                        LISTED_VEHICLES AS LV
                    JOIN 
                        BIDDINGS AS B ON LV.listing_id = B.listing_id
                    WHERE 
                        B.bidding_date BETWEEN %s AND %s
                    GROUP BY 
                        LV.listing_id
                ) AS ranked_listings
                WHERE 
                    bid_rank <= 5;
            """, [vehicle_start_date, vehicle_end_date])
            popular_vehicles = cursor.fetchall()

    top_sellers = None
    # Fetch top sellers data
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH RankedUsers AS (
                SELECT
                    user_id,
                    user_name,
                    seller_rating,
                    num_of_seller_rating,
                    DENSE_RANK() OVER (ORDER BY seller_rating DESC) AS user_rank
                FROM USERS
                WHERE user_type = 'NORMAL_USER' AND seller_rating != 0
            )
            SELECT 
                user_id, 
                user_name, 
                seller_rating, 
                num_of_seller_rating
            FROM RankedUsers
            WHERE user_rank <= 10
            ORDER BY seller_rating DESC, num_of_seller_rating DESC;
        """)
        top_sellers = cursor.fetchall()

    print(start_date)
    print(end_date)
    print(vehicle_start_date)
    print(vehicle_end_date)
    context = {
        'user_type': user_type,
        'user_name': user_name,
        'current_page': 'weekly_reports',
        'report_data': report_data,
        'start_date': start_date,
        'end_date': end_date,
        'top_sellers': top_sellers,
        'popular_vehicles': popular_vehicles,
        'vehicle_start_date': vehicle_start_date,
        'vehicle_end_date': vehicle_end_date,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'weekly_reports.html', context)


def other_user_profile(request, other_user_id):
    # enable write commnets
    handle_comment_submission(request)

    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')
    is_seller = request.session.get('is_seller', '')

    try:
        with connection.cursor() as cursor:
            # Fetch user's user_type
            cursor.execute(
                "SELECT user_type FROM USERS WHERE user_id = %s",
                [other_user_id])
            other_user_type = cursor.fetchone()

            # Check if the other user is ADMIN
            if other_user_type and other_user_type[0] == 'ADMIN':
                return HttpResponseForbidden("Admin User, Access Denied")

            # Fetch user details
            cursor.execute(
                "SELECT user_name, seller_rating, buyer_rating, num_of_seller_rating, num_of_buyer_rating FROM USERS WHERE user_id = %s",
                [other_user_id])
            other_user_details = cursor.fetchone()
            print(other_user_details)

            # Fetch listed vehicles
            if other_user_details:
                cursor.execute(
                    "SELECT listing_id, make, model, year_of_production, image_url FROM LISTED_VEHICLES WHERE seller_id = %s",
                    [other_user_id])
                listed_vehicles = cursor.fetchall()

    except Exception as e:
        print(f"An error occurred: {e}")
        # Return a 404 response for missing user ID
        return HttpResponseNotFound("404 User not found")

    if other_user_details is None:
        # Return a 404 response for missing user ID
        return HttpResponseNotFound("404 User not found")

    context = {
        "other_user_id": other_user_id,
        'user_details': other_user_details,
        'listed_vehicles': listed_vehicles,
        'user_type': user_type,
        'user_name': user_name,
        'is_seller': is_seller,
    }
    return render(request, 'other_user_profile.html', context)


def search_car(request):
    # enable write commnets
    handle_comment_submission(request)

    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    # Fetching data from the session
    user_id = request.session.get('user_id', '')

    # Fetch unique values for dropdowns from the database
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT DISTINCT make FROM LISTED_VEHICLES ORDER BY make")
        makes = [row[0] for row in cursor.fetchall()]

        cursor.execute(
            "SELECT DISTINCT year_of_production FROM LISTED_VEHICLES ORDER BY year_of_production")
        years = [row[0] for row in cursor.fetchall()]

        cursor.execute(
            "SELECT DISTINCT mileage FROM LISTED_VEHICLES ORDER BY mileage")
        mileages = [row[0] for row in cursor.fetchall()]

        cursor.execute(
            "SELECT DISTINCT price FROM LISTED_VEHICLES ORDER BY price")
        prices = [row[0] for row in cursor.fetchall()]

    error_message = None

    # Fetch filter parameters
    make = request.GET.get('make')
    min_year = request.GET.get('min_year')
    max_year = request.GET.get('max_year')
    min_mileage = request.GET.get('min_mile')
    max_mileage = request.GET.get('max_mile')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Check for invalid filter ranges
    if min_year and max_year and int(min_year) > int(max_year):
        error_message = "Minimum year cannot be greater than maximum year."
    elif min_mileage and max_mileage and int(min_mileage) > int(max_mileage):
        error_message = "Minimum mileage cannot be greater than maximum mileage."
    elif min_price and max_price and int(min_price) > int(max_price):
        error_message = "Minimum price cannot be greater than maximum price."

    # If there's an error, return early with the error message
    if error_message:
        return render(request, 'search_car.html', {'error_message': error_message})

    # Initialize the base query
    query = "SELECT * FROM LISTED_VEHICLES WHERE listing_status = TRUE AND is_verified = TRUE"

    # Initialize the parameters list
    params = []

    # Append conditions to the query based on provided filters
    if make:
        query += " AND make = %s"
        params.append(make)

    if min_year:
        query += " AND year_of_production >= %s"
        params.append(min_year)

    if max_year:
        query += " AND year_of_production <= %s"
        params.append(max_year)

    if min_mileage:
        query += " AND mileage >= %s"
        params.append(min_mileage)

    if max_mileage:
        query += " AND mileage <= %s"
        params.append(max_mileage)

    if min_price:
        query += " AND price >= %s"
        params.append(min_price)

    if max_price:
        query += " AND price <= %s"
        params.append(max_price)

    # Fetch the search term
    search_words = []
    search_term = request.GET.get('search_term', '').strip()

    # Check if search term is not empty
    if search_term:
        search_words = search_term.split()

    # Initialize search_words as an empty list
    search_words = []

    # Fetch the search term
    search_term = request.GET.get('search_term', '').strip()

    # Check if search term is not empty
    if search_term:
        search_words = search_term.split()

        # Build the search query only if there are search words
        search_query = " AND ("
        search_query_parts = []
        for word in search_words:
            search_query_parts.append(
                "(make LIKE %s OR model LIKE %s OR exterior_color LIKE %s OR "
                "vehicle_description LIKE %s OR fuel_type LIKE %s OR CAST(year_of_production AS CHAR) LIKE %s)")
            params.extend(["%" + word + "%"] * 6)

        # Only append if there are parts to the search query
        if search_query_parts:
            search_query += " OR ".join(search_query_parts) + ")"
            query += search_query

    vehicles = []
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        for row in cursor.fetchall():
            vehicles.append(dict(zip(columns, row)))

    user_name = request.session.get('user_name', '')
    user_type = request.session.get('user_type', '')
    is_seller = request.session.get('is_seller', '')

    return render(request, 'search_car.html', {
        'user_name': user_name,
        'user_type': user_type,
        'is_seller': is_seller,
        'vehicles': vehicles,
        'makes': makes,
        'years': years,
        'mileages': mileages,
        'prices': prices,
        'error_message': error_message,
        'current_page': 'search_car',
    })


def product_detail(request, listing_id):
    # enable write commnets
    handle_comment_submission(request)

    result = None
    current_bid = None

    with connection.cursor() as cursor:
        # SQL query to join USERS and LISTED_VEHICLES tables
        cursor.execute("""
            SELECT LV.*, U.*
            FROM LISTED_VEHICLES AS LV
            JOIN USERS AS U ON LV.seller_id = U.user_id
            WHERE LV.listing_id = %s
        """, [listing_id])

        result = cursor.fetchone()

    # If no product is found, raise a 404 error
    if not result:
        raise Http404("Product does not exist")

    user_id = request.session.get('user_id', '')
    current_user_id = user_id
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT bidding_amount FROM BIDDINGS
                WHERE listing_id = %s AND user_id = %s
                ORDER BY bidding_date DESC
                LIMIT 1
            """, [listing_id, current_user_id])
        current_bid = cursor.fetchone()

    # Map the result to a dictionary for easy access in the template
    product_dict = {
        'listing_id': result[0],
        'VIN': result[1],
        'image_url': result[3],
        'vehicle_description': result[4],
        'make': result[5],
        'model': result[6],
        'fuel_type': result[7],
        'year_of_production': result[8],
        'mileage': result[9],
        'price': result[10],
        'exterior_color': result[11],
        'interior_color': result[12],
        'state': result[13],
        'zip_code': result[14],
        'seller_id': result[19],
        'seller_name': result[21],
        'seller_rating': result[24],
        'current_bid': current_bid[0] if current_bid else None,
        'is_active': result[18],
    }
    # print("19")
    # print(result[19])
    # print("18")
    # print(result[18])
    # print("17")
    # print(result[17])
    # print("16")
    # print(result[16])
    # return render(request, 'product_detail.html', {'product': product_dict})
    if request.method == 'POST' and 'bid_amount' in request.POST:
        bid_amount = request.POST.get('bid_amount')
        # Assuming user authentication
        user_id = request.user.id

        # Convert bid amount to a decimal or float as needed
        bid_amount = float(bid_amount)

        # Insert the bid into the database
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO BIDDINGS (listing_id, user_id, bidding_amount, bidding_date)
                VALUES (%s, %s, %s, NOW())
            """, [listing_id, user_id, bid_amount])
            # If the bid is successfully placed, add a success message
            messages.success(request, 'Bid placed successfully!')
            # Redirect to the same page to display the success message
            return redirect('bid_success', listing_id=listing_id, user_id=request.user.id)

    user_id = request.session.get('user_id', '')
    user_name = request.session.get('user_name', '')
    user_type = request.session.get('user_type', '')
    is_seller = request.session.get('is_seller', '')
    is_allowed_chat = get_is_allowed_chat(user_id)

    # Add new chat
    seller_id = result[19]
    is_active = result[18]
    current_user_id = request.session.get('user_id', '')

    if add_new_chat(request, listing_id, user_id, seller_id):
        return redirect('product_detail', listing_id=listing_id)

    # Get chat history
    chat_history = get_chat_history(listing_id, current_user_id, seller_id)

    # For GET requests or if the bid placement is not successful, render the page with product details
    return render(request, 'product_detail.html', {
        'product': product_dict,
        'user_name': user_name,
        'user_type': user_type,
        'user_id': user_id,
        'seller_id': seller_id,
        'chat_history': chat_history,
        'is_seller': is_seller,
        'is_allowed_chat': is_allowed_chat,
        'is_active': is_active,
    })


def get_is_allowed_chat(user_id):
    with connection.cursor() as cursor:
        query = "SELECT is_allowed_chat FROM USERS WHERE user_id = %s"
        cursor.execute(query, [user_id])

        row = cursor.fetchone()

        if row is not None:
            # row[0] will be the is_allowed_chat value
            return row[0]
        else:
            return None  # or handle as appropriate


def get_chat_history(listing_id, buyer_id, seller_id):
    chat_messages = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM CHATS
            WHERE listing_id = %s 
            AND ((sender_id = %s AND receiver_id = %s) 
            OR (sender_id = %s AND receiver_id = %s))
            ORDER BY date ASC
        """, [listing_id, buyer_id, seller_id, seller_id, buyer_id])
        chat_messages = cursor.fetchall()
    return chat_messages


def add_new_chat(request, listing_id, buyer_id, seller_id):
    new_message_added = False
    if request.method == 'POST' and 'new_message' in request.POST:
        sender_id = buyer_id
        receiver_id = seller_id
        new_message = request.POST.get('new_message')
        if new_message:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO CHATS (sender_id, receiver_id, message, date, listing_id)
                    VALUES ( %s, %s, %s, NOW(), %s)
                """, [sender_id, receiver_id, new_message, listing_id])
            new_message_added = True

        return new_message_added


def bid(request, listing_id):
    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    user_id = request.session.get('user_id', '')

    # enable write commnets
    handle_comment_submission(request)

    #  # Check if there is already a winner for this listing
    # is_winner = False
    # with connection.cursor() as cursor:
    #     cursor.execute("""
    #         SELECT is_winner FROM BIDDINGS
    #         WHERE listing_id = %s AND is_winner = TRUE
    #     """, [listing_id])
    #     is_winner = cursor.fetchone() is not None

    if request.method == 'POST':
        # if is_winner:
        #     # If there is already a winner, redirect to an error page or show a message.
        #     return HttpResponse('This listing already has a winning bid and is closed for further bidding.', status=403)

        try:
            bid_amount = float(request.POST['bid_amount'])

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT price FROM LISTED_VEHICLES WHERE listing_id = %s", [listing_id])
                product_price = cursor.fetchone()
                if not product_price or bid_amount < product_price[0]:
                    # Handle bid amount lower than product price
                    return render(request, 'error.html', {'error_message': 'Bid amount must be higher than the product price'})

                cursor.execute("SELECT MAX(bidding_id) FROM BIDDINGS")
                max_id_result = cursor.fetchone()
                new_bidding_id = max_id_result[0] + \
                    1 if max_id_result[0] else 1

                cursor.execute("""
                    INSERT INTO BIDDINGS (bidding_id, listing_id, user_id, bidding_amount, bidding_date, is_winner)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [new_bidding_id, listing_id, user_id, bid_amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None])
                connection.commit()

            return redirect('product_detail', listing_id=listing_id)
        except IntegrityError as e:
            print(e)
            # Handle the error, perhaps show a message to the user

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT LV.*, U.*
            FROM LISTED_VEHICLES AS LV
            JOIN USERS AS U ON LV.seller_id = U.user_id 
            WHERE LV.listing_id = %s
        """, [listing_id])

        result = cursor.fetchone()

    user_name = request.session.get('user_name', '')
    user_type = request.session.get('user_type', '')

    product_dict = {
        'user_name': user_name,
        'user_type': user_type,
        'image_url': result[3],
        'make': result[5],
        'model': result[6],
        'price': result[10],

    }

    user_name = request.session.get('user_name', '')
    user_type = request.session.get('user_type', '')
    is_seller = request.session.get('is_seller', '')

    return render(request, 'bid.html', {
        'product': product_dict,
        'listing_id': listing_id,
        'user_name': user_name,
        'user_type': user_type,
        'is_seller': is_seller,
        'current_page': 'product_detail',

    })


def chatbot(request):
    # enable write commnets
    handle_comment_submission(request)

    user_name = request.session.get('user_name', '')
    user_type = request.session.get('user_type', '')
    is_seller = request.session.get('is_seller', '')

    return render(request, 'chatbot.html', {
        'user_name': user_name,
        'user_type': user_type,
        'is_seller': is_seller,
        'current_page': 'chatbot',
    })


@csrf_exempt
@require_POST
def chat(request):
    data = json.loads(request.body)
    user_message = data.get('message')

    # You need to configure your OpenAI API key
    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        return JsonResponse({'response': response.choices[0].message['content']})
    except Exception as e:
        return JsonResponse({'response': str(e)}, status=500)


# def bid_success(request, listing_id):
#     # need modification
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SELECT *
#             FROM BIDDINGS
#             WHERE listing_id = %s
#         """, [listing_id])

#         result = cursor.fetchone()

#     # Map the result to a dictionary for easy access in the template
#     bidding_dict = {
#         'bidding_amount': result[3],
#     }

#     return render(request, 'bid.html', {'bidding': bidding_dict})

# # views.py


def buyer_rate_seller(request, order_id):
    user_id = request.session.get('user_id', None)
    user_name = request.session.get('user_name', '')
    user_type = request.session.get('user_type', '')
    is_seller = request.session.get('is_seller', '')

    # Initialize existing_rating to None
    existing_rating = None

    # Retrieve listing_id, seller_id, and winner_id from the order
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT listing_id, seller_id, buyer_id FROM VEHICLE_ORDERS
            WHERE order_id = %s;
        """, [order_id])
        order_details = cursor.fetchone()

    if order_details:
        listing_id, seller_id, winner_id = order_details

        if user_id != winner_id:
            return HttpResponseForbidden("Access denied: You are not the buyer for this order.")

        # Check if the rating already exists
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT rate FROM RATINGS
                WHERE listing_id = %s AND seller_id = %s AND winner_id = %s
                AND seller_rate_from_winner = TRUE;
            """, [listing_id, seller_id, winner_id])
            existing_rating = cursor.fetchone()
    else:
        return HttpResponseForbidden("Access denied: No Such Order.")

    if request.method == 'POST' and order_details:
        rate = request.POST.get('rate')

        with connection.cursor() as cursor:
            if existing_rating:
                # Update the existing rating
                cursor.execute("""
                    UPDATE RATINGS SET rate = %s
                    WHERE listing_id = %s AND seller_id = %s AND winner_id = %s
                    AND seller_rate_from_winner = TRUE;
                """, [rate, listing_id, seller_id, winner_id])
            else:
                # Insert a new rating
                cursor.execute("""
                    INSERT INTO RATINGS (listing_id, seller_id, winner_id, seller_rate_from_winner, winner_rate_from_seller, rate)
                    VALUES (%s, %s, %s, TRUE, FALSE, %s);
                """, [listing_id, seller_id, winner_id, rate])
            return redirect('orders')  # Redirect to the orders page or another appropriate page

    return render(request, 'buyer_rate_seller.html', {
        'user_name': user_name,
        'user_type': user_type,
        'order_id': order_id,
        'is_seller': is_seller,
        'existing_rating': existing_rating[0] if existing_rating else None,
    })


# post new vehicle listings
def sell_post(request):
    handle_comment_submission(request)

    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    user_id = request.session.get('user_id', '')
    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')
    is_seller = request.session.get('is_seller', '')
    is_allow_list = request.session.get('is_allow_list', '')

    if request.method == 'POST':
        vin = request.POST.get('vin')
        image_url = request.POST.get('image_url')
        vehicle_description = request.POST.get('vehicle_description')
        make = request.POST.get('make')
        model = request.POST.get('model')
        fuel_type = request.POST.get('fuel_type')
        year_of_production = request.POST.get('year_of_production')
        mileage = request.POST.get('mileage')
        price = request.POST.get('price')
        exterior_color = request.POST.get('exterior_color')
        interior_color = request.POST.get('interior_color')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        listing_end_date = request.POST.get('listing_end_date')

        try:
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO LISTED_VEHICLES (VIN, seller_id, image_url, vehicle_description, make, model, fuel_type, year_of_production, mileage, price, exterior_color, interior_color, state, zip_code, listing_start_date, listing_end_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s);
                """
                print(query)
                cursor.execute(query, (vin, user_id, image_url, vehicle_description, make, model, fuel_type,
                               year_of_production, mileage, price, exterior_color, interior_color, state, zip_code, listing_end_date))
                connection.commit()
                return redirect('sell_post_success')
        except Exception as e:
            print(f"An error occurred: {e}")
            # Optionally, add feedback for the user here

    return render(request, 'sell_post.html', {
        'user_type': user_type,
        'user_name': user_name,
        'user_id': user_id,
        'is_seller': is_seller,
        "is_allow_list": is_allow_list,
        'current_page': 'sell_post',
    })


# post new vehicle listings successful
def sell_post_success(request):
    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    user_id = request.session.get('user_id', '')
    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')
    is_seller = request.session.get('is_seller', '')

    return render(request, 'sell_post_success.html', {
        'user_type': user_type,
        'user_name': user_name,
        'user_id': user_id,
        'is_seller': is_seller,
        'current_page': 'sell_post_success',
    })

# Chat with buyer view function


def chat_with_buyer(request):
    handle_comment_submission(request)
    unique_token = int(time.time())

    current_user_id = request.session.get('user_id', '')
    chats = []
    chat_history = []
    selected_listing_id = None
    selected_buyer_name = None
    selected_buyer_id = None
    message_submitted = False
    is_allowed_chat = get_is_allowed_chat(current_user_id)

    # Handling message submission
    if request.method == 'POST' and 'new_message' in request.POST:
        form_token = request.POST.get('form_token')
        if request.session.get('last_form_token') != form_token:
            request.session['last_form_token'] = form_token
            selected_listing_id = request.POST.get('selected_listing_id')
            selected_buyer_name = request.POST.get('selected_buyer_name')
            selected_buyer_id = request.POST.get('selected_buyer_id')
            if add_new_chat(request, selected_listing_id, current_user_id, selected_buyer_id):
                selected_listing_id = request.session.get('selected_listing_id', '')
                sender = request.session.get('sender', '')
                receiver = request.session.get('receiver', '')
                chat_history = get_chat_history(selected_listing_id, sender, receiver)
                redirect('chat_with_buyer')

    # Handling chat selection
    if request.method == 'POST' and 'selected_listing_id' in request.POST:
        selected_listing_id = request.POST.get('selected_listing_id')
        selected_buyer_name = request.POST.get('selected_buyer_name')
        selected_buyer_id = request.POST.get('selected_buyer_id')
        request.session['sender'] = current_user_id
        request.session['receiver'] = selected_buyer_id
        request.session['selected_listing_id'] = selected_listing_id
        chat_history = get_chat_history(selected_listing_id, current_user_id, selected_buyer_id)
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.chat_id, 
                c.message, 
                c.date, 
                c.listing_id, 
                u.user_name, 
                u.user_id
            FROM 
                CHATS c
            JOIN 
                USERS u ON c.sender_id = u.user_id
            JOIN 
                (SELECT 
                    MAX(date) as latest_date, 
                    listing_id,
                    sender_id
                FROM 
                    CHATS
                WHERE 
                    receiver_id = %s
                GROUP BY 
                    listing_id, sender_id) AS latest_messages ON c.date = latest_messages.latest_date AND c.listing_id = latest_messages.listing_id AND c.sender_id = latest_messages.sender_id
            WHERE 
                c.receiver_id = %s AND 
                c.listing_id IN 
                    (SELECT listing_id FROM LISTED_VEHICLES WHERE seller_id = %s)
            ORDER BY 
                c.listing_id, c.sender_id, c.date DESC;
        """, [current_user_id, current_user_id, current_user_id])
        chats = cursor.fetchall()

    user_id = request.session.get('user_id', '')
    print('user_id')
    print(user_id)
    user_type = request.session.get('user_type', '')
    user_name = request.session.get('user_name', '')
    is_seller = request.session.get('is_seller', '')

    return render(request, 'chat_with_buyer.html', {
        'user_type': user_type,
        'user_name': user_name,
        'user_id': user_id,
        'is_seller': is_seller,
        'chats': chats,
        'selected_listing_id': selected_listing_id,
        'selected_buyer_name': selected_buyer_name,
        'selected_buyer_id': selected_buyer_id,
        'chat_history': chat_history,
        'is_allowed_chat': is_allowed_chat,
        'unique_token': unique_token,
        'current_page': 'chat_with_buyer',
    })


def choose_bid(request, listing_id):
    user_email = request.session.get('email', '')
    if user_email:
        update_session(request, user_email)

    user_id = request.session.get('user_id', '')
    user_name = request.session.get('user_name', '')
    user_type = request.session.get('user_type', '')

    # Check if the listing already has a winning bid
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT is_winner
            FROM BIDDINGS
            WHERE listing_id = %s AND is_winner = TRUE
        """, [listing_id])
        winner_exists = cursor.fetchone() is not None

    # Fetch bid details using listing_id
    bids_list = []
    if not winner_exists:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    b.bidding_id,
                    b.user_id,
                    b.bidding_amount,
                    b.bidding_date,
                    u.user_name,
                    u.balance,
                    (u.balance - b.bidding_amount >= 0) AS enough_money_to_pay
                FROM 
                    BIDDINGS b
                JOIN 
                    USERS u ON b.user_id = u.user_id
                WHERE 
                    b.listing_id = %s
                ORDER BY 
                    b.bidding_amount DESC
            """, [listing_id])
            bids = cursor.fetchall()
            if bids:
                for bid in bids:
                    bids_list.append({
                        'bidding_id': bid[0],
                        'user_id': bid[1],
                        'bidding_amount': bid[2],
                        'bidding_date': bid[3].strftime("%Y-%m-%d %H:%M:%S"),
                        'user_name': bid[4],
                        'balance': bid[5],
                        'enough_money_to_pay': bid[6]
                    })
    if request.method == 'POST':
        # Get bidding_id from the POST request
        bidding_id = request.POST.get('bidding_id')

        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT user_id, bidding_amount
                    FROM BIDDINGS
                    WHERE bidding_id = %s;
                """, [bidding_id])
            bid = cursor.fetchone()
        if bid:
            buyer_id, order_price = bid
            seller_id = request.session.get('user_id')

        # update listing_status to not active
        with connection.cursor() as cursor:
            cursor.execute("""
                    UPDATE LISTED_VEHICLES
                    SET listing_status = FALSE
                    WHERE listing_id = %s;
                    """, (listing_id))

        # Insert transaction data for seller
        with connection.cursor() as cursor:
            transaction_type1 = 'receive'
            cursor.execute("""
                    INSERT INTO BALANCE_TRANSACTIONS (user_id, current_balance, date, transaction_type, transaction_amount)
                    VALUES (%s, (SELECT balance FROM USERS WHERE user_id = %s), NOW(), %s, %s);
                    """, (seller_id, seller_id,  transaction_type1, order_price))
        with connection.cursor() as cursor:
            # Insert transaction data for buyer
            transaction_type2 = 'pay'
            cursor.execute("""
                        INSERT INTO BALANCE_TRANSACTIONS (user_id, current_balance, date, transaction_type, transaction_amount)
                        VALUES (%s, (SELECT balance FROM USERS WHERE user_id = %s), NOW(), %s, %s);
                    """, (buyer_id, buyer_id,  transaction_type2, order_price))
        with connection.cursor() as cursor:
            # Update balance in USERS table for seller
            cursor.execute("""
                        UPDATE USERS
                        SET balance = balance + %s
                        WHERE user_id = %s;
                    """, (order_price, seller_id))

            # Update balance in USERS table for buyer
            cursor.execute("""
                        UPDATE USERS
                        SET balance = balance - %s
                        WHERE user_id = %s;
                    """, (order_price, buyer_id))

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE BIDDINGS
                SET is_winner = FALSE
                WHERE listing_id = %s;
            """, [listing_id])

        # Set the chosen bid as the winning bid
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE BIDDINGS
                SET is_winner = TRUE
                WHERE bidding_id = %s;
            """, [bidding_id])

    # Generate a random tracking number
        tracking_number = random.randint(10000, 99999)
        is_paid = True
        is_shipped = True

        # generate order record
        with connection.cursor() as cursor:
            #     cursor.execute("SELECT MAX(order_id) FROM VEHICLE_ORDERS;")
            #     max_id = cursor.fetchone()[0]
            #     new_order_id = max_id + 1 if max_id else 1

            # Insert order into VEHICLE_ORDERS
            cursor.execute("""
                    INSERT INTO VEHICLE_ORDERS (listing_id, buyer_id, seller_id, order_price, order_date, tracking_number, is_paid, is_shipped)
            VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s);
            """, (listing_id, buyer_id, user_id, order_price, tracking_number, is_paid, is_shipped))
        with connection.cursor() as cursor:
            # Update all biddings to not be the winner
            cursor.execute("""
                    UPDATE BIDDINGS
                    SET is_winner = FALSE
                    WHERE listing_id = %s;
            """, [listing_id])
        with connection.cursor() as cursor:
            # Set the selected bid as the winner
            cursor.execute("""
                    UPDATE BIDDINGS
                    SET is_winner = TRUE
                    WHERE bidding_id = %s;
                """, [bidding_id])

            return redirect('profile')

    # If GET request or no bid has been selected, render the page with bid options
    return render(request, 'choose_bid.html', {
        'winner_exists': winner_exists,
        'bids_list': bids_list,
        'user_type': user_type,
        'user_name': user_name,
        'user_id': user_id,
        'listing_id': listing_id,
    })


def seller_rate_buyer(request, listing_id):
    user_id = request.session.get('user_id', None)
    user_name = request.session.get('user_name', '')
    user_type = request.session.get('user_type', '')

    rating_exists = False
    current_rating = None

    # Track if the user is the seller of the vehicle
    try:
        with connection.cursor() as cursor:
            # Validate if the listing_id exists in LISTED_VEHICLES
            cursor.execute(
                "SELECT COUNT(*) FROM LISTED_VEHICLES WHERE listing_id = %s", [listing_id])
            if cursor.fetchone()[0] == 0:
                return HttpResponseForbidden("Listing not found.")

            # Fetch seller_id for the listing
            cursor.execute(
                "SELECT seller_id FROM LISTED_VEHICLES WHERE listing_id = %s", [listing_id])
            seller_id = cursor.fetchone()[0]

            # Check if the logged-in user is the seller
            if user_id == seller_id:
                is_seller = True
            else:
                return HttpResponseForbidden("You are not the seller.")
    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        with connection.cursor() as cursor:
            # Check if a rating already exists
            cursor.execute("""
                SELECT rate FROM RATINGS
                WHERE listing_id = %s AND seller_id = %s AND seller_rate_from_winner = %s AND winner_rate_from_seller = %s
            """, [listing_id, user_id, False, True])
            result = cursor.fetchone()
            if result:
                rating_exists = True
                current_rating = result[0]
    except Exception as e:
        print(f"An error occurred while checking existing rating: {e}")

    if request.method == 'POST' and not rating_exists:
        rate = request.POST.get('rate')

        try:
            with connection.cursor() as cursor:
                # Fetch the buyer_id from VEHICLE_ORDERS
                cursor.execute(
                    "SELECT buyer_id FROM VEHICLE_ORDERS WHERE listing_id = %s", [listing_id])
                buyer_id = cursor.fetchone()[0]

                # Insert the rating
                cursor.execute("""
                    INSERT INTO RATINGS (listing_id, seller_id, winner_id, seller_rate_from_winner, winner_rate_from_seller, rate)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (listing_id, user_id, buyer_id, False, True, rate))

        except Exception as e:
            print(f"An error occurred while inserting the rating: {e}")
            # Handle the error

        return redirect('profile')

    return render(request, 'seller_rate_buyer.html', {
        'user_id': user_id,
        'user_name': user_name,
        'listing_id': listing_id,
        'user_type': user_type,
        'rating_exists': rating_exists,
        'current_rating': current_rating
    })
