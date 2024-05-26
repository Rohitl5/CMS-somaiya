from django.shortcuts import render
from .models import Conference


    # Retrieve all conference objects from the database
conferences = Conference.objects.all()

    # Print all conference objects
for conference in conferences:
        print("Conference ID:", conference.id)
        print("Conference Title:", conference.conferenceTitle)
        # Print other conference attributes as needed
    
   
