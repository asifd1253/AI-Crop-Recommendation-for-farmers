from django.urls import path
from .views import *

urlpatterns = [
    path("",home, name="home"),
    path("signup/",signup_view, name="signup"),
    path("predict/",predict_view, name="predict"),
    path("autopredict/",autopredict_view, name="autopredict"),
    path("logout/",logout_view, name="logout"),
    path("login/",login_view, name="login"),
    path("user_history/",user_history_view, name ="user_history"),
    path("delete_prediction/<int:id>/",delete_prediction_view, name ="delete_prediction"),
    path("update_profile/",update_profile_view, name ="update_profile"),
    path("change_pass/",change_pass_view, name ="change_pass"),
    path("admin_login/",admin_login_view, name ="admin_login"),
    path("admin_dashboard/",admin_dashboard_view, name ="admin_dashboard"),
    path("admin_user_details/",admin_user_details, name ="admin_user_details"),
    path("delete_user/<int:id>/",delete_user_view, name ="delete_user"),
    path("admin_predictions/",admin_predictions_view, name ="admin_predictions"),
    path("admin_delete_prediction/<int:id>/",admin_delete_prediction_view, name ="admin_delete_prediction"),
]