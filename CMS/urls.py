from django.urls import path
from . import views

from Project import settings

app_name = "CMS"
urlpatterns = [ path('', views.index, name='index'),
                path('conferences/', views.conferences, name='conferences'),
                path('signup/', views.signup, name='signup'),
                path('login/', views.login_view, name='login'),
                path('profile/', views.profile, name='profile'),
                path('logout/', views.logout_view, name='logout'),
                path('authrs-view/',views.author,name="authors-view"),
                path('reviewer-view/',views.reviewer,name="reviewer-view"),
                path('programChair-view/',views.programChair,name="programChair-view"),]