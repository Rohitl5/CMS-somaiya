from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect,HttpResponseForbidden
from .models import Conference,committeeImages,conferenceImages,Track,Author,Reviewer,Paper,Review
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


user=get_user_model()
def index(request):
    conferences = Conference.objects.all().values()
    return render(request, 'index.html',{"conferences":conferences})

def signup(request):
    if request.method == 'POST':
            formal_title = request.POST["designation"]
            first_name= request.POST["fname"]
            last_name= request.POST["lname"]
            email= request.POST["email"]
            phone= request.POST["phone"]
            prof= request.POST['profession']
            afiliation=request.POST['afiliation']
            role=request.POST['role']
            password = request.POST["pass"]
            cpassword=request.POST["cpass"]
            if password==cpassword:
             User = user.objects.create_user(formal_title=formal_title,first_name=first_name,last_name=last_name,email=email,phone=phone,profession=prof,afiliation=afiliation,role=role,password=password)
             User.save()
             login(request, User)
             return redirect('CMS:profile')
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
            email=request.POST["email"]
            password=request.POST["pass"]
            user = authenticate(request,email=email,password=password)
            if user is not None:
             login(request, user) 
             return redirect('CMS:profile')
            else:
                raise ValueError("Invalid credentials")
    return render(request, 'login.html')

@login_required
def profile(request):
    conferences = Conference.objects.values()
    enrolled=Conference.objects.filter(programChair=request.user).values()
    return render(request, 'profile.html',context={"conferences":conferences,"enrolled":enrolled})

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

# Views for program chair

@login_required
def programChair(request,conference_id):
    conference = get_object_or_404(Conference, id=conference_id)
    authors= Author.objects.filter(conferences=conference)
    papers=Paper.objects.filter(conference=conference)
    reviewers = Reviewer.objects.filter(conference=conference)
    reviews= Review.objects.all()
    
    if not conference.is_chair(request.user):
        return HttpResponseForbidden('You are not authorized.')
    else:
        return render(request, 'program_chair.html',context={"conference":conference,"authors":authors,"uploadedpapers":papers,"reviewers":reviewers,"reviews":reviews})

def conferences(request,conference_id):
    conference = get_object_or_404(Conference, conferenceTitle=conference_id)
    tracks= Track.objects.filter(conference_id=conference.id).all().values()

    return render(request, 'view_conferences.html',context={"conference":conference,"tracks":tracks})

def add_conference(request):
    if user.is_authenticated:
     if request.method=='POST':
        title=request.POST['title']
        institute=request.POST['institute']
        aboutInstitute=request.POST['aboutInstitute']
        aboutConference=request.POST['aboutConference']
        submission_deadline = request.POST['submissionDeadline']
        notification_of_acceptance = request.POST['notificationOfAcceptance']
        registration_deadline=request.POST['registrationDeadline']
        camera_ready_papers=request.POST['cameraReadyPapers']
        conference_date=request.POST['conferenceDate']
        conference_venue=request.POST['venue']
        committee_images=request.FILES.getlist('committeeImages')
        conference_images=request.FILES.getlist('conferenceImages')

        conference=Conference.objects.create(conferenceTitle=title,
                                             programChair=request.user,
                                             organizing_institute=institute,
                                             institute_details=aboutInstitute,
                                             about_conference=aboutConference,
                                             submission_deadline=submission_deadline,
                                             notification_of_acceptance=notification_of_acceptance,
                                             registration_deadline=registration_deadline,
                                             camera_ready_papers=camera_ready_papers,
                                             conference_date=conference_date,
                                             conference_venue=conference_venue
                                             )
        conference.save()
        for image1 in committee_images:
            committee_images=committeeImages.objects.create(
                conference=conference,
                committee_image=image1
            )
            committee_images.save()
        
        for image2 in conference_images:
            conference_images=conferenceImages.objects.create(
                conference=conference,
                conference_image=image2
            )
            committee_images.save()

        return redirect('/conference/'+str(conference.id)+'/programChair/')
     else:
         return HttpResponseRedirect(request.path_info)
    else:
        return render(request,'login.html')

def edit_conference(request,conference_id):
    if request.method=='POST':
       
       aboutInstitute=request.POST['aboutInstitute']
       aboutConference=request.POST['aboutConference']
       submission_deadline = request.POST['submissionDeadline']
       notification_of_acceptance = request.POST['notificationOfAcceptance']
       registration_deadline=request.POST['registrationDeadline']
       camera_ready_papers=request.POST['cameraReadyPapers']
       conference_date=request.POST['conferenceDate']
       conference_venue=request.POST['venue']
       committee_images=request.FILES.getlist('committeeImages')
       conference_images=request.FILES.getlist('conferenceImages') 
       
       
       Conference.objects.filter(id=conference_id).update(
                         institute_details=aboutInstitute,
                         about_conference=aboutConference,
                         submission_deadline=submission_deadline,
                         notification_of_acceptance=notification_of_acceptance,
                         registration_deadline=registration_deadline,
                         camera_ready_papers=camera_ready_papers,
                         conference_date=conference_date,
                         conference_venue=conference_venue
                         )
       for image1 in committee_images:
            committee_images=committeeImages.objects.create(
                conference=Conference.objects.filter(id=conference_id),
                committee_image=image1
            )
            committee_images.save()
        
       for image2 in conference_images:
            conference_images=conferenceImages.objects.create(
                conference=Conference.objects.filter(id=conference_id),
                conference_image=image2
            )
            committee_images.save()

       return redirect('/conference/'+str(conference_id)+'/programChair/')

@login_required
def addTrack(request,conference_id):
    if request.method=="POST":
       trackName=request.POST["title"]
       subDomains=request.POST["subDomains"]
       conference=Conference.objects.get(id=conference_id)
       track = Track.objects.create(conference=conference,title=trackName,subDomains=subDomains)
       track.save()
       return redirect('/conference/'+str(conference_id)+'/programChair/')

def inviteReviewer(request,conference_id):
    if request.method=="POST":
        reviewer_email=request.POST["reviewer_email"]
        conference_title=Conference.objects.filter(id=conference_id).values_list("conferenceTitle",flat=True)[0]
        
        subject = 'Invitation to '+conference_title
        message = 'Respected Sir/Madam,\n You are invited to join "'+conference_title+'"\nSteps for the same are\n1. Click on the link: http://127.0.0.1:8000/conference/{{conference.id}}\n2. Click on "Join as" and select "Reviewer"\n\nThankyou'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [reviewer_email ]
        send_mail( subject, message, email_from, recipient_list )
        return redirect('/conference/'+str(conference_id)+'/programChair/')

def author_request(request,conference_id):
    if user.is_authenticated:
          conference= Conference.objects.get(id=conference_id)
          
          subject = 'Request to join as an author'
          message = 'Respected Program Chair,\n'+str(request.user.first_name)+' '+str(request.user.last_name)+' has request to enter "'+str(conference.conferenceTitle)+'"\nAuthor Deatils are:\nEmail- '+str(request.user.email)+'\nProfession- '+str(request.user.profession)+'\nAfiliated to '+str(request.user.afiliation)+' as '+str(request.user.role)+'\nTo add author click on the link: http://127.0.0.1:8000/conference/'+str(conference.id)+'/add_author='+str(request.user.id)+'/\n\nThankyou'
          email_from = settings.EMAIL_HOST_USER
          recipient_list = [conference.programChair ]
          send_mail( subject, message, email_from, recipient_list )
          return redirect('/conference/'+str(conference.conferenceTitle))
    else:
        return render(request,'login.html')
    
def reviewer_request(request,conference_id):
    if user.is_authenticated:
          if request.method=="POST":
           conference= Conference.objects.get(id=conference_id)
           areaOfInterest=request.POST["areaOfInterest"]

           subject = 'Request to join as an reviewer'
           message = 'Respected Program Chair,\n'+str(request.user.first_name)+' '+str(request.user.last_name)+' has request to enter "'+str(conference.conferenceTitle)+'"\nReviewer Deatils are:\nEmail- '+str(request.user.email)+'\nProfession- '+str(request.user.profession)+'\nAfiliated to '+str(request.user.afiliation)+' as '+str(request.user.role)+'\nHis\Hers Area of interests are '+areaOfInterest+'\nTo add reviewer click on the link: http://127.0.0.1:8000/conference/'+str(conference_id)+'/add_reviewer='+str(request.user.id)+'/\n\nThankyou'
           email_from = settings.EMAIL_HOST_USER
           recipient_list = [conference.programChair ]
           send_mail( subject, message, email_from, recipient_list )
           return redirect('/conference/'+str(conference.conferenceTitle))
    else:
        return render(request,'login.html')
    
@login_required
def add_author(request,conference_id,user_id):
    conference = get_object_or_404(Conference, id=conference_id)
    
    if not conference.is_chair(request.user):
        return HttpResponseForbidden("You are not authorized to add authors to this conference.")
    author = user.objects.get(id=user_id)
    
    new_author=Author.objects.create(user=author)
    new_author.conferences.add(conference)

    new_author.save()
    return redirect('/conference/'+str(conference_id)+'/programChair/')  

@login_required
def add_reviewer(request,conference_id,user_id):
    conference = get_object_or_404(Conference, id=conference_id)

    if not conference.is_chair(request.user):
        return HttpResponseForbidden("You are not authorized to add reviewers to this conference.")
    
    reviewer = user.objects.get(id=user_id)
    new_reviewer=Reviewer.objects.create(user=reviewer,conference=conference)
    new_reviewer.save()

    return redirect('/conference/'+str(conference_id)+'/programChair/')  

@login_required
def accept_paper(request,review_id,conference_id):
    review = get_object_or_404(Review, id=review_id)
    conference = get_object_or_404(Conference, id=conference_id)
    paper = get_object_or_404(Paper,id=review.paper.id)

    paper.status="accepted"
    review.result="accepted"
    paper.save()
    review.save()
    return redirect('/conference/' + str(conference.id) + '/programChair/')

@login_required
def reject_paper(request,review_id,conference_id):
    review = get_object_or_404(Review, id=review_id)
    conference = get_object_or_404(Conference, id=conference_id)
    paper=get_object_or_404(Paper,id=review.paper.id)
    review.result="rejected"
    paper.status="rejected"
    paper.save()
    review.save()
    return redirect('/conference/' + str(conference.id) + '/programChair/')

@login_required
def author(request,conference_id):
    conference = get_object_or_404(Conference, id=conference_id)
    author=Author.objects.get(user=request.user)
    # is_author=Author.objects.filter(user=request.user,conferences=conference).exists()
    # if is_author:
    tracks= Track.objects.filter(conference_id=conference.id).all().values()
    papers=Paper.objects.filter(authors=author).all().values()
    paper_names=Paper.objects.filter(authors=author).all().values('id')
    reviews_for_submittedpapers = Review.objects.filter(paper__in=paper_names)
    print(reviews_for_submittedpapers)

    # for submitting paper 
    if request.method=="POST":
      title = request.POST['title']
      abstract = request.POST['abstract']
      file = request.FILES['paper']
      conf = conference
      track = get_object_or_404(Track,title=request.POST["track"])
      authors = get_object_or_404(Author,user=request.user)
      status = 'submitted'
      keywords= request.POST['keywords']
      submissionDate= timezone.now().date() 
      otherauthors=request.POST['other-authors']

      if otherauthors=='none':
          otherauthors=None
      
      paper=Paper.objects.create(papertitle = title,
            abstract = abstract,
            file = file,
            conference = conf,
            track = track,
            authors = authors,
            status = status,
            keywords= keywords,
            submissionDate= submissionDate,
            otherauthors=otherauthors   )
      paper.save()
      return redirect('/conference/'+str(conference_id)+'/author/')
    
    return render(request, 'authrs-view.html',context={"conference":conference,"tracks":tracks,"uploadedpapers":papers,"reviews":reviews_for_submittedpapers})
    # else:
    #     # The user is not an author for this conference
    #      return HttpResponseForbidden("You are not authorized as an author in this conference. To join as author select 'join as author' on the conference main page.")
   
@login_required
def reviewer(request,conference_id):
    conference = get_object_or_404(Conference, id=conference_id)
    reviewer=Reviewer.objects.get(user=request.user)
    papers=Paper.objects.filter(reviewer=reviewer).exclude(review__isnull=False)
    reviews=Review.objects.filter(reviewer=reviewer)
    context={"conference":conference,"papers":papers,"reviews":reviews}
    return render(request, 'reviewer-view.html',context)

@login_required
def submitreview(request,conference_id,paper_id):
    paper=Paper.objects.get(id=paper_id) 
    reviewer=Reviewer.objects.get(user=request.user)
    relevance = request.POST["relevance"]
    writingStyle = request.POST["writingstyle"]
    reviewerConfidence = request.POST["resultanalysis"]
    
    result=None
    modeOfPreapartion=request.POST["modeofpreparation"]
    score = request.POST["overallevaluation"]
    comments = request.POST["comments"]
    confidentialremarks=request.POST["remarks"]

    review=Review.objects.create(
    paper = paper,
    reviewer = reviewer,
    relevance = relevance,
    writingStyle = writingStyle,
    reviewerConfidence = reviewerConfidence,
    
    result=result,
    modeOfPreparation= modeOfPreapartion,
    score = score,
    comments = comments,
    confidentialremarks=confidentialremarks
    )
    review.save()
    return redirect('/conference/' + str(conference_id) + '/reviewer/')

@login_required
def assign_reviwer(request,paper_id,conference_id):
    paper = get_object_or_404(Paper, id=paper_id)
    conference = get_object_or_404(Conference, id=conference_id)

    # Check if the user is the program chair for the conference
    if not conference.is_chair(request.user):
        return HttpResponseForbidden("You are not authorized to assign a reviewer to this paper.")

    if request.method == "POST":
        reviewer_id = request.POST.get("reviewer")
        if reviewer_id:
            reviewer = get_object_or_404(Reviewer, id=reviewer_id)
            paper.reviewer = reviewer
            paper.status="under_review"
            paper.save()
            return redirect('/conference/' + str(conference.id) + '/programChair/')
        else:
            return HttpResponseForbidden("Invalid reviewer selection.")
    