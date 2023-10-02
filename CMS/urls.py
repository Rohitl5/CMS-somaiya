from django.urls import path
from . import views

from Project import settings

app_name = "CMS"
urlpatterns = [ path('', views.index, name='index'),
                path('signup/', views.signup, name='signup'),
                path('login/', views.login_view, name='login'),
                path('profile/', views.profile, name='profile'),
                path('logout/', views.logout_view, name='logout'),
                path('conference/<int:conference_id>', views.conferences, name='conference'),
                
                path('conference/<int:conference_id>/programChair/',views.programChair,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/addTrack/',views.addTrack,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/editConference/',views.edit_conference,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/inviteReviewer/',views.inviteReviewer,name="programChair-view"),

                path('authrs-view/',views.author,name="authors-view"),
                path('reviewer-view/',views.reviewer,name="reviewer-view"),
                path('add_conference/',views.add_conference,name="add_conference")]