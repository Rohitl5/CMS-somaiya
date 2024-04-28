from django.urls import path
from . import views

from Project import settings

app_name = "CMS"
urlpatterns = [ path('', views.index, name='index'),
                path('signup/', views.signup, name='signup'),
                path('login/', views.login_view, name='login'),
                path('profile/', views.profile, name='profile'),
                path('logout/', views.logout_view, name='logout'),
                path('add_conference/',views.add_conference,name="add_conference"),
                path('conference/<str:conference_id>', views.conferences, name='conference'),
                
                
                path('conference/<int:conference_id>/programChair/',views.programChair,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/addTrack/',views.addTrack,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/editConference/',views.edit_conference,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/inviteReviewer/',views.inviteReviewer,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/paper=<int:paper_id>/',views.assign_reviewer,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/accept_paper/<int:paper_id>',views.accept_paper,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/reject_paper/<int:paper_id>',views.reject_paper,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/export_data/<int:choice>',views.export_data,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/desktop_reject/<int:paper_id>',views.desktop_reject,name="programChair-view"),
                path('conference/<int:conference_id>/programChair/reject_due_to_plagarism/<int:paper_id>',views.reject_due_to_plagiarism,name="programChair-view"),

                path('conference/<int:conference_id>/request_author/',views.author_request,name="conference"),
                path('conference/<int:conference_id>/add_author=<int:user_id>/',views.add_author,name="authors-view"),
                path('conference/<int:conference_id>/author/',views.author,name="authors-view"),
                path('conference/<int:conference_id>/author/submit_paper/',views.author,name="authors-view"),
                path('conference/<int:conference_id>/author/resubmit_paper/<int:paper_id>',views.resubmit_paper,name="authors-view"),
                path('conference/<int:conference_id>/author/unsubmit_paper=<int:paper_id>/',views.unsubmitPaper,name="authors-view"),
                path('conference/<int:conference_id>/author/register_author/',views.register_author,name="authors-view"),

                path('conference/<int:conference_id>/request_reviewer/',views.reviewer_request,name="conference"),
                path('conference/<int:conference_id>/add_reviewer=<int:user_id>/',views.add_reviewer,name="reviewer-view"),
                path('conference/<int:conference_id>/reviewer/',views.reviewer,name="reviewer-view"),
                path('conference/<int:conference_id>/reviewer/submitreview/paper=<int:paper_id>/',views.submitreview,name="reviewer-view"),
                
]