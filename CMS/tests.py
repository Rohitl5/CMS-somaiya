from django.shortcuts import render
from .models import Conference,Reviewer,Paper

paper = Paper.objects.all()
for p in paper:
    assigned_reviewers = p.reviewers.all()
    print(f"Assigned reviewers for paper '{p.papertitle}': {assigned_reviewers}")

    
   
