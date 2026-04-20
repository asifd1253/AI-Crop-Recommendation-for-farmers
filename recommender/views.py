from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def home(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_predictions = Prediction.objects.count()
    return render(request, "home.html",locals())

def signup_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not name or not phone or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("signup")
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("signup")
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect("signup")
        user = User.objects.create_user(username=email, password=password)
        if " " in name:
            first, last = name.split(" ",1)
        else:
            first,last = name, ""
        user.first_name, user.last_name = first, last
        user.save()
        UserProfile.objects.create(user=user, phone=phone)
        messages.success(request, "Account created successfully. Please login.")
        login(request, user)
        return redirect("predict")
    return render(request, "signup.html")

from .ml.loader import predict_crop, load_bundle
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required(login_url="login")
def predict_view(request):
    features_order = load_bundle()["features_cols"]
    result = None
    last_data = None

    if request.method == "POST":
        data = {}
        try:
            for c in features_order:
                data[c] = float(request.POST.get(c))
        except ValueError:
            messages.error(request, "Please enter valid numeric values for all features.")
            return redirect("predict")       
        
        result = predict_crop(data)
        Prediction.objects.create(user=request.user,**data,predicted_label=result)

        last_data = data
        messages.success(request, f"Predicted Crop: {result}")

    return render(request, "predict.html",locals())

import requests
import random
def get_sensor_data():
    url = "https://api.thingspeak.com/channels/3316777/feeds.json?api_key=MV1MNHKIOYL77CAU&results=1"

    response = requests.get(url)
    data = response.json()

    latest = data["feeds"][-1]

    rain_raw = float(latest["field4"])

    # 🔥 Real sensor data
    sensor_data = {
        "ph": float(latest["field1"]),
        "temperature": float(latest["field2"]),
        "humidity": float(latest["field3"]),
        "rainfall": round((4095 - rain_raw) / 4095 * 100, 2)
    }

    # 🔥 Generate NPK values (simulated)
    npk_data = {
        "N": random.randint(0, 100),
        "P": random.randint(0, 100),
        "K": random.randint(0, 100),
    }

    # 🔥 Merge both
    final_data = {**npk_data, **sensor_data}

    return final_data


@login_required(login_url="login")
def autopredict_view(request):
    features_order = load_bundle()["features_cols"]
    result = None
    last_data = None

    # 🔹 get real sensor data
    sensor_data = get_sensor_data()

    # 🔹 prepare full data (ML expects N, P, K also)
    api_data = {
        **sensor_data
    }

    # 🔹 if user submits form
    if request.method == "POST":
        data = {}
        try:
            for c in features_order:
                data[c] = float(request.POST.get(c))
        except ValueError:
            messages.error(request, "Please enter valid numeric values.")
            return redirect("autopredict")

        result = predict_crop(data)

        Prediction.objects.create(
            user=request.user,
            **data,
            predicted_label=result
        )

        last_data = data
        messages.success(request, f"Predicted Crop: {result}")

    return render(request, "autopredict.html", locals())



def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if not user:
            messages.error(request,"Invalid credentials!")
            return redirect("login")
        else:
            login(request, user)
            messages.success(request, "Loggedin successful")
            return redirect("predict")
    return render(request, "login.html")

@login_required(login_url="login")
def user_history_view(request):
    
    predictions = Prediction.objects.filter(user=request.user)
    return render(request, "user_history.html",locals())


@login_required(login_url="login")
def delete_prediction_view(request, id):
    try:
        pred = Prediction.objects.get(id=id, user=request.user)
        pred.delete()
        messages.success(request, "Prediction deleted successfully.")
    except Prediction.DoesNotExist:
        messages.error(request, "Prediction not found or you don't have permission to delete it.")
    return redirect("user_history")

def update_profile_view(request):
    profile = UserProfile.objects.get(user=request.user)
    full_name = request.user.get_full_name()
   
    if request.method == 'POST':
        name = request.POST.get("name")
        phone = request.POST.get("phone")

        if not name or not phone:
            messages.error(request, "All fields are required.")
            return redirect("update_profile")
        
        if " " in name:
            first, last = name.split(" ",1)
        else:
            first,last = name, ""
        
        request.user.first_name, request.user.last_name = first, last
        request.user.save()

        profile.phone = phone
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("update_profile")   #this is the path link then after the path link the page will call by using function
    return render(request, "update_profile.html",locals())

def change_pass_view(request):
    profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")

        if not old_password or not new_password:
            messages.error(request, "All fields are required.")
            return redirect("change_pass")
        
        if not request.user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
            return redirect("change_pass")
        
        if len(new_password) < 6:
            messages.error(request, "New password must be at least 6 characters long.")
            return redirect("change_pass")
        
        request.user.set_password(new_password)
        request.user.save()

        messages.success(request, "Password changed successfully. Please login again.")
        logout(request)
        return redirect("login")   #this is the path link then after the path link the page will call by using function
    return render(request, "change_pass.html",locals())


def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and not user.is_staff:
            messages.error(request,"You don't have admin access!")
            return redirect("admin_login")
        elif not user:
            messages.error(request,"Invalid credentials!")
            return redirect("admin_login")
        else:
            login(request, user)
            messages.success(request, "Admin Logedin successful")
            return redirect("admin_dashboard")
    return render(request, "admin_login.html")

from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import json

@user_passes_test(lambda u: u.is_staff, login_url="admin_login")
def admin_dashboard_view(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_predictions = Prediction.objects.count()

    crop_details = Prediction.objects.values('predicted_label').annotate(count = Count('id')).order_by('-count')[:10]

    crop_labels = [c['predicted_label'] for c in crop_details]
    crop_counts = [c['count'] for c in crop_details]

    today = timezone.localdate()

    # create a list of last 7 dates (including today)
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    day_labels = [d.strftime("%d %b") for d in last_7_days]

    day_counts = [
        Prediction.objects.filter(created_at__date=d).count()
        for d in last_7_days
    ]

    context = {
        "total_users": total_users,
        "total_predictions": total_predictions,
        "crop_labels_json": json.dumps(crop_labels),
        "crop_counts_json": json.dumps(crop_counts),
        "day_labels_json": json.dumps(day_labels),
        "day_counts_json": json.dumps(day_counts),
    }

    return render(request, "admin_dashboard.html", context)

@user_passes_test(lambda u: u.is_staff, login_url="admin_login")
def admin_user_details(request):
    users = User.objects.filter(is_staff=False)
    
    return render(request, "admin_user_details.html", locals())

@user_passes_test(lambda u: u.is_staff, login_url="admin_login")
def delete_user_view(request, id):
    try:
        user = User.objects.get(id=id)
        user.delete()
        messages.success(request, "User deleted successfully.")
    except User.DoesNotExist:
        messages.error(request, "User not found or you don't have permission to delete it.")
    return redirect("admin_user_details")

@user_passes_test(lambda u: u.is_staff, login_url="admin_login")
def admin_predictions_view(request):
    qs = Prediction.objects.select_related('user')

    curCrop = request.GET.get("crop")
    startDate = request.GET.get("start_date")
    endDate = request.GET.get("end_date")

    if curCrop:
        qs = qs.filter(predicted_label__iexact=curCrop)

    if startDate:
        qs = qs.filter(created_at__date__gte=startDate)

    if endDate:
        qs = qs.filter(created_at__date__lte=endDate)

    tot_crops = (Prediction.objects.order_by('predicted_label').values_list('predicted_label',flat=True).distinct())
    context = {
        'qs':qs,
        'tot_crops':tot_crops,
        'curCrop':curCrop,
        'startDate':startDate,
        'endDate':endDate,
    }

    return render(request, "admin_predictions.html",context)


@user_passes_test(lambda u: u.is_staff, login_url="admin_login")
def admin_delete_prediction_view(request, id):
    try:
        pred = Prediction.objects.get(id=id)
        pred.delete()
        messages.success(request, "Prediction deleted successfully.")
    except Prediction.DoesNotExist:
        messages.error(request, "Prediction not found or you don't have permission to delete it.")
    return redirect("admin_predictions")