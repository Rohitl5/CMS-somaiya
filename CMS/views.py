from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect,HttpResponseForbidden
from .models import Conference,committeeImages,conferenceImages,Track,Author,Reviewer
from django.conf import settings
from django.core.mail import send_mail

user=get_user_model()
def index(request):
    conferences = Conference.objects.all().values()
    return render(request, 'index.html',{"conferences":conferences})


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


def inviteReviewer(request,conference_id):
    if request.method=="POST":
        reviewer_email=request.POST["reviewer_email"]
        conference_title=Conference.objects.filter(id=conference_id).values_list("conferenceTitle",flat=True)[0]
        
        subject = 'Invitation to '+conference_title
        message = 'Respected Sir/Madam,\n You are invited to join "'+conference_title+'"\nSteps for the same are\n1. Click on the link: http://127.0.0.1:8000/conference/5\n2. Click on "Join as" and select "Reviewer"\n\nThankyou'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [reviewer_email ]
        send_mail( subject, message, email_from, recipient_list )
        return redirect('/conference/'+str(conference_id)+'/programChair/')


def author_request(request,conference_id):
    if user.is_authenticated:
          conference= Conference.objects.get(id=conference_id)
          
          subject = 'Request to join as an author'
          message = 'Respected Program Chair,\n'+str(request.user.first_name)+' '+str(request.user.last_name)+' has request to enter "'+str(conference.conferenceTitle)+'"\nAuthor Deatils are:\nEmail- '+str(request.user.email)+'\nProfession- '+str(request.user.profession)+'\nAfiliated to '+str(request.user.afiliation)+' as '+str(request.user.role)+'\nTo add author click on the link: http://127.0.0.1:8000/conference/5/add_author='+str(request.user.id)+'/\n\nThankyou'
          email_from = settings.EMAIL_HOST_USER
          recipient_list = [conference.programChair ]
          send_mail( subject, message, email_from, recipient_list )
          return redirect('/conference/'+str(conference_id))
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

def reviewer_request(request,conference_id):
    if user.is_authenticated:
          if request.method=="POST":
           conference= Conference.objects.get(id=conference_id)
           areaOfInterest=request.POST["areaOfInterest"]

           subject = 'Request to join as an reviewer'
           message = 'Respected Program Chair,\n'+str(request.user.first_name)+' '+str(request.user.last_name)+' has request to enter "'+str(conference.conferenceTitle)+'"\nReviewer Deatils are:\nEmail- '+str(request.user.email)+'\nProfession- '+str(request.user.profession)+'\nAfiliated to '+str(request.user.afiliation)+' as '+str(request.user.role)+'\nHis\Hers Area of interests are '+areaOfInterest+'\nTo add reviewer click on the link: http://127.0.0.1:8000/conference/5/add_reviewer='+str(request.user.id)+'/\n\nThankyou'
           email_from = settings.EMAIL_HOST_USER
           recipient_list = [conference.programChair ]
           send_mail( subject, message, email_from, recipient_list )
           return redirect('/conference/'+str(conference_id))
    else:
        return render(request,'login.html')

@login_required
def add_reviewer(request,conference_id,user_id):
    conference = get_object_or_404(Conference, id=conference_id)

    if not conference.is_chair(request.user):
        return HttpResponseForbidden("You are not authorized to add reviewers to this conference.")
    
    reviewer = user.objects.get(id=user_id)
    new_reviewer=Reviewer.objects.create(user=reviewer)
    new_reviewer.save()

    return redirect('/conference/'+str(conference_id)+'/programChair/')  

@login_required
def author(request,conference_id):
    return render(request, 'authrs-view.html')

@login_required
def reviewer(request,conference_id):
    return render(request, 'reviewer-view.html')

@login_required
def programChair(request,conference_id):
    conference = get_object_or_404(Conference, id=conference_id)
    authors= Author.objects.filter(conferences=conference).all().values()
    if not conference.is_chair(request.user):
        return HttpResponseForbidden('You are not authorized.')
    else:
        return render(request, 'program_chair.html',context={"conference":conference,"authors":authors})

@login_required
def addTrack(request,conference_id):
    if request.method=="POST":
       trackName=request.POST["title"]
       subDomains=request.POST["subDomains"]
       conference=Conference.objects.get(id=conference_id)
       track = Track.objects.create(conference=conference,title=trackName,subDomains=subDomains)
       track.save()
       return redirect('/conference/'+str(conference_id)+'/programChair/')


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
            print(request.POST)
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
    return render(request, 'profile.html',{"conferences":conferences})

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')
