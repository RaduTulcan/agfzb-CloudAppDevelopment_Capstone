from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealers_reviews_from_cf, get_dealer_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import random

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        logging.error(username)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/organizationMine_djangoserver-space/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        context["dealership_list"] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/organizationMine_djangoserver-space/dealership-package/get-review"
        reviews = get_dealers_reviews_from_cf(url, dealer_id)
        dealership = get_dealer_by_id_from_cf("https://eu-de.functions.appdomain.cloud/api/v1/web/organizationMine_djangoserver-space/dealership-package/get-dealership", dealer_id)
        context["reviews"] = reviews
        context["dealership"] = dealership[0]

        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == 'GET':
        context = {}
        dealership = get_dealer_by_id_from_cf("https://eu-de.functions.appdomain.cloud/api/v1/web/organizationMine_djangoserver-space/dealership-package/get-dealership", dealer_id)
        context["dealership"] = dealership[0]
        cars = CarModel.objects.all()
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == 'POST':
        if request.user.is_authenticated:
            payload = {}
            username = request.user.username
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = dealer_id
            payload["id"] = random.randint(100, 100000)
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
                payload["purchase_date"] = request.POST["purchasedate"]
                payload["car_make"] = car.car_make.name
                payload["car_model"] = car.name
                payload["car_year"] = int(car.year.strftime("%Y"))
                review_post_url = "https://eu-de.functions.appdomain.cloud/api/v1/web/organizationMine_djangoserver-space/dealership-package/post-review"
                post_request(review_post_url, payload, id=dealer_id)
                return redirect("djangoapp:dealer_details", dealer_id=dealer_id)