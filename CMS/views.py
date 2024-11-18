from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
import os
import csv
from django.core.mail import EmailMessage
from django.contrib import messages
from openpyxl import Workbook
from django.http import HttpResponseRedirect,HttpResponseForbidden,HttpResponse
from .models import Conference,committeeImages,conferenceImages,Track,Author,Reviewer,Paper,Review,registered_authors
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.core.files.storage import FileSystemStorage


user=get_user_model()
def index(request):
    if request.user.is_authenticated:
        return redirect('profile/')
    else:
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
                # Check if password matches confirm password
            if password != cpassword:
                messages.error(request, "Passwords do not match. Please try again.")
                return render(request, 'signup.html')
    
            # Use get to retrieve an existing user or None
            existing_user = user.objects.get(email=email) if user.objects.filter(email=email).exists() else None
    
            if existing_user is None:
                # User does not exist, create a new one
                new_user = user.objects.create_user(
                    formal_title=formal_title,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    profession=prof,
                    afiliation=afiliation,
                    role=role,
                    password=password
                )
                login(request, new_user)
                messages.info(request, "Signed-up Successfully!")
                return redirect('CMS:profile')
            else:
                # User with this email already exists
                messages.error(request, "User with this email already exists. Please use a different email.")
                return render(request, 'signup.html')
    
    return render(request, 'signup.html')
    
def login_view(request):
    if request.method == 'POST':
            email=request.POST["email"]
            password=request.POST["pass"]
            user = authenticate(request,email=email,password=password)
            if user is not None:
             login(request, user) 
             messages.info(request,"Login Successfull")
             return redirect('/profile/')
            else:
             messages.info(request,"Invalid Credentials")
             return redirect('/login/')
    return render(request, 'login.html')

@login_required
def profile(request):
    conferences = Conference.objects.values()
    enrolled_as_programChair=Conference.objects.filter(programChair=request.user).values()
    enrolled_as_author= Conference.objects.filter(author__user=request.user)
    enrolled_as_reviewer= Conference.objects.filter(reviewer__user=request.user)
    permission =0
    if request.user.is_authenticated:
        euser = user.objects.filter(id=request.user.id).values('id', 'email').first()
        if euser:
            specific_email = "rohit15@somaiya.edu"  # replace with the specific email you want to have the permission to create conference
            if euser['email'] == specific_email:
                permission=1;
    
    return render(request, 'profile.html',context={"conferences":conferences,"enrolled_as_programChair":enrolled_as_programChair,"enrolled_as_author":enrolled_as_author,"enrolled_as_reviewer":enrolled_as_reviewer,"permission":permission})

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
    # for paper in papers:
    #  if paper.otherauthors:
    #     other_authors_list = paper.otherauthors.split(',')  # Split by commas 
    #  else : other_authors_list =""
    tracks = Track.objects.filter(conference=conference) 

    reviewers = Reviewer.objects.filter(conference=conference)
    reviews= Review.objects.all()
    
    if not conference.is_chair(request.user):
        return HttpResponseForbidden('You are not authorized.')
    else:
        return render(request, 'program_chair.html',context={"conference":conference,"authors":authors,"uploadedpapers":papers,"reviewers":reviewers,"reviews":reviews,"tracks":tracks})


def conferences(request,conference_id):
     
    cc=conference_id.strip()   
    global ccc
    global c2
    conf = Conference.objects.all()
    for c in conf:
        cccc=c.conferenceTitle.strip()
        if(cccc==cc):
         c2=c.id
        


    conference=Conference.objects.get(id=c2)
    print(conference)
    # conference = get_object_or_404(Conference, conferenceTitle=conference_id)          //this might be most probable code but i found it not working for some cases so i replaced it with the one above
    tracks= Track.objects.filter(conference_id=conference.id).all().values()
    org=committeeImages.objects.filter(conference=conference.id)
    img=conferenceImages.objects.filter(conference=conference.id) 

    return render(request, 'view_conferences.html',context={"conference":conference,"tracks":tracks,"org":org,"img":img,})


def add_conference(request):
    if request.user.is_authenticated:
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
            conference_images.save()
        
        messages.info(request,"Conference created successfully and you are the program chair now !")
        return redirect('/conference/'+str(conference.id)+'/programChair/')
     else:
         return HttpResponseRedirect(request.path_info)
    else:
        messages.error(request,"Kindly Login First")
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
        conference_instance = Conference.objects.get(id=conference_id)
        committee_image = committeeImages.objects.create(
        conference=conference_instance,
        committee_image=image1
        )
        committee_image.save()
        
       for image2 in conference_images:
          conference = Conference.objects.get(id=conference_id)  # Get the conference instance
          new_image = conferenceImages(conference=conference, conference_image=image2)
          new_image.save()
    
         
       
       messages.info(request,"Changes made to the conference successfully")
       return redirect('/conference/'+str(conference_id)+'/programChair/')

@login_required
def addTrack(request,conference_id):
    if request.method=="POST":
       trackName=request.POST["title"]
       subDomains=request.POST["subDomains"]
       conference=Conference.objects.get(id=conference_id)
       track = Track.objects.create(conference=conference,title=trackName,subDomains=subDomains)
       track.save()
       messages.success(request,"Track added successfully")
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
        messages.info(request,"An invitation mail has been sent to the reviewers")
        return redirect('/conference/'+str(conference_id)+'/programChair/')

def author_request(request,conference_id):
    
    # if  request.user.is_authenticated:
    #       author_exists=Author.objects.filter(user=request.user).exists()
    #       conference= Conference.objects.get(id=conference_id)

    # the below code snippets check for if author for confernece exists 
    if request.user.is_authenticated:
          try:
                    conference = Conference.objects.get(id=conference_id)
          except Conference.DoesNotExist:
                    messages.error(request, "Conference not found.")
                    return redirect('/conferences/')

          author_exists = Author.objects.filter(user=request.user, conferences=conference).exists()



          if author_exists :
           messages.info(request,"You are already an author. ")
           return redirect('/conference/'+str(conference_id)+'/author/')
          if timezone.localtime(timezone.now()).date() > conference.registration_deadline:
           messages.info(request,"You can't register now as the registration deadline is over. ")
           return redirect('/conference/'+str(conference.conferenceTitle))  
          else :
            ####   here we can send mail to program chair if want two step authentication

        #    subject = 'Request to join as an author'
        #    message = 'Respected Program Chair,\n'+str(request.user.first_name)+' '+str(request.user.last_name)+' has request to enter "'+str(conference.conferenceTitle)+'"\nAuthor Deatils are:\nEmail- '+str(request.user.email)+'\nProfession- '+str(request.user.profession)+'\nAfiliated to '+str(request.user.afiliation)+' as '+str(request.user.role)+'\nTo add author click on the link: http://192.168.200.114:8000/conference/'+str(conference.id)+'/add_author='+str(request.user.id)+'/\n\nThankyou'
        #    email_from = settings.EMAIL_HOST_USER
        #    recipient_list = [conference.programChair ]
        #    send_mail( subject, message, email_from, recipient_list )
        #    messages.info(request,"Request sent to the Program Chair.Once he/she accepts the request you will be made author in the conference automatically.")
        #    return redirect('/conference/'+str(conference.conferenceTitle))
          
        ####  we dont need two step authentication
                  conferencee = get_object_or_404(Conference, id=conference_id)
                  author = user.objects.get(id=request.user.id)
                
                  new_author=Author.objects.create(user=author)
                  new_author.conferences.add(conferencee)

                  new_author.save()
                  messages.info(request,"You are added as an Author.")
                  return redirect('/conference/'+str(conference_id)+'/author/')  

    else:
        return render(request,'login.html')
    
def reviewer_request(request,conference_id):
    if request.user.is_authenticated:
        if request.method=="POST":
           try:
                 conference = Conference.objects.get(id=conference_id)
           except Conference.DoesNotExist:
                    messages.error(request, "Conference not found.")
                    return redirect('/conferences/')
           reviewer_exists=Reviewer.objects.filter(user=request.user, conference=conference).exists()
          
           if reviewer_exists :
            messages.info(request,"You are already a reviewer in this conference. ")
            return redirect('/conference/'+str(conference_id)+'/reviewer/')  
           else :
            conference= Conference.objects.get(id=conference_id)
            areaOfInterest=request.POST["areaOfInterest"]
            subject = 'Request to join as an reviewer'
            message = 'Respected Program Chair,\n'+str(request.user.first_name)+' '+str(request.user.last_name)+' has request to enter "'+str(conference.conferenceTitle)+'"\nReviewer Deatils are:\nEmail- '+str(request.user.email)+'\nProfession- '+str(request.user.profession)+'\nAfiliated to '+str(request.user.afiliation)+' as '+str(request.user.role)+'\nHis\Hers Area of interests are '+areaOfInterest+'\nTo add reviewer click on the link: http://192.168.43.114:8000/conference/'+str(conference_id)+'/add_reviewer='+str(request.user.id)+'/\n\nThankyou'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [conference.programChair ]
            send_mail( subject, message, email_from, recipient_list )
            messages.info(request,"Request sent to the Program Chair.Once he/she accepts the request you will be made reviewer in the conference automatically.")
            return redirect('/conference/'+str(conference.conferenceTitle))
    else:
         return render(request,'login.html')
    

# ### here author is added by programchair
    
@login_required
def add_author(request,conference_id,user_id):
    conference = get_object_or_404(Conference, id=conference_id)
    
    if not conference.is_chair(request.user):
        return HttpResponseForbidden("You are not authorized to add authors to this conference.")
    author = user.objects.get(id=user_id)
    
    new_author=Author.objects.create(user=author)
    new_author.conferences.add(conference)

    new_author.save()
    messages.info(request,"New author added successfully.")
    return redirect('/conference/'+str(conference_id)+'/programChair/')  

@login_required
def register_author(request,conference_id):
    conference= get_object_or_404(Conference,id=conference_id)
    if timezone.localtime(timezone.now()).date() > conference.registration_deadline:
           messages.info(request,"You can't register now as the registration deadline is over. ")  
    else:
           author = get_object_or_404(Author,user=request.user)
           register=registered_authors.objects.create(
              author=author,
              conference=conference
           )
           register.save()
           messages.info(request,"You registered successfully.")
    return redirect('/conference/'+str(conference_id)+'/author/')  

@login_required
def add_reviewer(request,conference_id,user_id):
    conference = get_object_or_404(Conference, id=conference_id)

    if not conference.is_chair(request.user):
        return HttpResponseForbidden("You are not authorized to add reviewers to this conference.")
    
    reviewer = user.objects.get(id=user_id)
    new_reviewer=Reviewer.objects.create(user=reviewer,conference=conference)
    new_reviewer.save()

    messages.info(request,"New reviewer added successfully.")
    return redirect('/conference/'+str(conference_id)+'/programChair/')  

@login_required
def assign_reviewer(request, paper_id, conference_id):
    paper = get_object_or_404(Paper, id=paper_id)
    conference = get_object_or_404(Conference, id=conference_id)

    # Check if the user is the program chair for the conference
    if not conference.is_chair(request.user):
        return HttpResponseForbidden("You are not authorized to assign reviewers to this paper.")

    if request.method == "POST":
        reviewer_ids = request.POST.getlist("reviewers")

        if reviewer_ids:
            reviewers = Reviewer.objects.filter(id__in=reviewer_ids)

             # Get the main author's email
            main_author_email = paper.authors.user.email

            # Get the list of other authors' emails
            other_authors_list = []
            if paper.otherauthors:
                other_authors_list = [email.strip() for email in paper.otherauthors.split(',')]

            # Check if any of the selected reviewers are also authors
            conflicting_reviewers = []
            for reviewer in reviewers:
                if reviewer.user.email == main_author_email or reviewer.user.email in other_authors_list:
                    conflicting_reviewers.append(f"{reviewer.user.first_name} {reviewer.user.last_name} ({reviewer.user.email})")

            if conflicting_reviewers:
                    # Add a warning message with the conflicting reviewers
                    conflict_message = (
                                    "The following selected reviewers are also authors or other authors:<br>"
                                    + "<br>".join([f"<span style='color: red;'>{reviewer}</span>" for reviewer in conflicting_reviewers])
)
                    messages.warning(request, conflict_message)
            else:
                    # If no conflicts, assign reviewers and update paper status
                    paper.reviewers.set(reviewers)
                    paper.status = "under_review"
                    paper.save()

                    assigned_reviewers = paper.reviewers.all()
                    print(f"Assigned reviewers for paper '{paper.papertitle}': {assigned_reviewers}")


                    # Notify each reviewer
                    for reviewer in reviewers:
                        subject = 'Request to review paper.'
                        message = f'Respected {reviewer.user.first_name} {reviewer.user.last_name},'\
                                f'\nYou have a new paper to be reviewed.\n\nThank you'
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [reviewer.user.email]
                        send_mail(subject, message, email_from, recipient_list)

                    messages.info(request, "Paper assigned to the reviewers successfully, and notifying emails have been sent.")
                    return redirect('/conference/' + str(conference.id) + '/programChair/') 
            
            return redirect('/conference/' + str(conference.id) + '/programChair/')
        else:
            return HttpResponseForbidden("Invalid reviewer selection.")
    
@login_required
def accept_paper(request,paper_id,conference_id):
    paper = get_object_or_404(Paper, id=paper_id)
    reviews = Review.objects.filter(paper=paper)
    conference = get_object_or_404(Conference, id=conference_id)
    
    for review in reviews:
        review.result = "accepted"
        review.save()
    paper.status="accepted"
    
    paper.save()
    
    return redirect('/conference/' + str(conference.id) + '/programChair/')

@login_required
def reject_paper(request,paper_id,conference_id):
    paper = get_object_or_404(Paper, id=paper_id)
    reviews = Review.objects.filter(paper=paper)
    conference = get_object_or_404(Conference, id=conference_id)

    for review in reviews:
        review.result = "rejected"
        review.save()
    
    paper.status="rejected"
    paper.save()
    
    return redirect('/conference/' + str(conference.id) + '/programChair/')

@login_required
def reject_due_to_plagiarism(request,conference_id, paper_id):
    conference = get_object_or_404(Conference, id=conference_id)
    if request.method == 'POST' and request.FILES['plagiarism_report']:
        plagiarism_report = request.FILES['plagiarism_report']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT , 'plagiarism_reports'))
        fs.save(plagiarism_report.name, plagiarism_report)
        plagiarism_report_path = os.path.join(settings.MEDIA_ROOT, 'plagiarism_reports', plagiarism_report.name)
        paper = Paper.objects.get(id=paper_id)
    
        paper.status="Rejected due to Plagarism"
        paper.save()
        
        subject = 'Paper rejected due to plagarism.'
        message = 'Respected Author,'+'\nYour paper '+str(paper.papertitle)+' has been rejected by the program chair as it was found that the paper has high plagarism .Kindly resubmit it.\nAttached herewith, is the plagarism report.\n\nThankyou'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [paper.authors ]
        email_message = EmailMessage(
        subject,
        message,
        email_from,
        recipient_list,
        )
        email_message.attach_file(plagiarism_report_path)

        email_message.send()
        messages.info(request,"Rejected successfully.")
        return redirect('/conference/' + str(conference.id) + '/programChair/')
    
    return redirect('/conference/' + str(conference.id) + '/programChair/')

@login_required
def desktop_reject(request,conference_id,paper_id):
   conference = get_object_or_404(Conference, id=conference_id)
   paper = get_object_or_404(Paper, id=paper_id)
   paper.status="Desktop Rejected"
   paper.save()
   
   subject = 'Paper desktop rejected.'
   message = 'Respected Author,'+'\n Your paper '+str(paper.papertitle)+' has been desktop rejected by the program chair.\n\nThankyou'
   email_from = settings.EMAIL_HOST_USER
   recipient_list = [paper.authors ]
   send_mail(subject,message,email_from,recipient_list)
   messages.info(request,"Desktop Rejected successfully.")
   return redirect('/conference/' + str(conference.id) + '/programChair/')

@login_required
def export_data(request,conference_id,choice):
 conference=get_object_or_404(Conference, id=conference_id)
 if choice==1:
    papers = Paper.objects.filter(conference_id=conference_id)
    
    if not papers:
     messages.error(request, 'No papers submitted for this conference.')
     return redirect('/conference/'+str(conference_id)+'/programChair/')
    else :
    
     response = HttpResponse(content_type='text/csv')
     response['Content-Disposition'] = f'attachment; filename=conference_{conference_id}_papers.csv'
 
     csv_writer = csv.writer(response)
     
     headers = ['Title', 'Abstract', 'Authors', 'Status', 'Submission Date', 'Keywords']
     csv_writer.writerow(headers)
 
     for paper in papers:
         author_email = paper.authors.user.email if paper.authors else 'No Author'
         row_data = [paper.papertitle, paper.abstract, author_email,
                     paper.status, paper.submissionDate, paper.keywords]
         csv_writer.writerow(row_data)
 
     return response

 if choice==2:
  reviewed_papers = Paper.objects.filter(conference=conference, status='accepted', review__isnull=False).distinct()
  if not reviewed_papers:
     messages.error(request, 'No papers reviewed yet .')
     return redirect('/conference/'+str(conference_id)+'/programChair/')
  else:  
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=reviewed_papers_{conference_id}.csv'

    csv_writer = csv.writer(response)
    csv_writer.writerow(['Paper Title', 'Abstract', 'Author(s)', 'Reviewer', 'Relevance', 'Writing Style',
                         'Reviewer Confidence', 'Result', 'Mode of Preparation', 'Score', 'Comments', 'Confidential Remarks'])

    for paper in reviewed_papers:
        review = Review.objects.get(paper=paper)
        csv_writer.writerow([
            paper.papertitle,
            paper.abstract,
            paper.authors.user.email,
            review.reviewer.user.email,
            review.relevance,
            review.writingStyle,
            review.reviewerConfidence,
            review.result,
            review.modeOfPreparation,
            review.score,
            review.comments,
            review.confidentialremarks,
        ])

    return response
 if choice==3:
  authors = Author.objects.filter(conferences=conference)
  reviewers = Reviewer.objects.filter(conference=conference)
  if not authors and not reviewers:
     messages.error(request, 'No peoples added to the conference yet .')
     return redirect('/conference/'+str(conference_id)+'/programChair/')
  else:  
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=author_reviewer_details_{conference_id}.csv'
    csv_writer = csv.writer(response)
    csv_writer.writerow(['Author Email', 'Author First Name', 'Author Last Name', 'Author Phone', 'Author Profession', 'Author Affiliation', 'Author Role','Submitted Papers'])
    for author in authors:
        submitted_papers = Paper.objects.filter(authors=author)
        csv_writer.writerow([
            author.user.email,
            author.user.first_name,
            author.user.last_name,
            author.user.phone,
            author.user.profession,
            author.user.afiliation,
            author.user.role,
            submitted_papers.count()
        ])

    csv_writer.writerow([])
    csv_writer.writerow(['Reviewer Email', 'Reviewer First Name', 'Reviewer Last Name', 'Reviewer Phone','Reviewed Papers'])
    for reviewer in reviewers:
        reviewed_papers = Paper.objects.filter(reviewer=reviewer)
        csv_writer.writerow([
            reviewer.user.email,
            reviewer.user.first_name,
            reviewer.user.last_name,
            reviewer.user.phone,
            reviewed_papers.count()
        ])

    return response
 if choice==4:
  
  reviewers = Reviewer.objects.filter(conference=conference)
  if not reviewers:
     messages.error(request, 'No reviewers added to the conference yet .')
     return redirect('/conference/'+str(conference_id)+'/programChair/')
  else:  
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=author_reviewer_details_{conference_id}.csv'
    csv_writer = csv.writer(response)
    csv_writer.writerow(['Reviewer Email', 'Reviewer First Name', 'Reviewer Last Name', 'Reviewer Phone','Reviewed Papers'])
    for reviewer in reviewers:
        reviewed_papers = Paper.objects.filter(reviewer=reviewer)
        csv_writer.writerow([
            reviewer.user.email,
            reviewer.user.first_name,
            reviewer.user.last_name,
            reviewer.user.phone,
            reviewed_papers.count()
        ])

    return response
  
 if choice==5:
  authors = Author.objects.filter(conferences=conference)
  
  if not authors :
     messages.error(request, 'No authors added to the conference yet .')
     return redirect('/conference/'+str(conference_id)+'/programChair/')
  else:  
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=author_reviewer_details_{conference_id}.csv'
    csv_writer = csv.writer(response)
    csv_writer.writerow(['Author Email', 'Author First Name', 'Author Last Name', 'Author Phone', 'Author Profession', 'Author Affiliation', 'Author Role','Submitted Papers'])
    for author in authors:
        submitted_papers = Paper.objects.filter(authors=author)
        csv_writer.writerow([
            author.user.email,
            author.user.first_name,
            author.user.last_name,
            author.user.phone,
            author.user.profession,
            author.user.afiliation,
            author.user.role,
            submitted_papers.count()
        ])

    return response
  
 if choice==6:
   authors = registered_authors.objects.filter(conference=conference)
  
   if not authors :
     messages.error(request, 'No authors registered to the conference yet .')
     return redirect('/conference/'+str(conference_id)+'/programChair/')
   else:  
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=registered_authors_details_{conference_id}.csv'
    csv_writer = csv.writer(response)
    csv_writer.writerow(['Author Email', 'Author First Name', 'Author Last Name', 'Author Phone', 'Author Profession', 'Author Affiliation', 'Author Role','Submitted Papers'])
    for author in authors:
        submitted_papers = Paper.objects.filter(authors=author.author)
        csv_writer.writerow([
            author.author.user.email,
            author.author.user.first_name,
            author.author.user.last_name,
            author.author.user.phone,
            author.author.user.profession,
            author.author.user.afiliation,
            author.author.user.role,
            submitted_papers.count()
        ])

    return response


# views for author
@login_required
def author(request,conference_id):
    conference = get_object_or_404(Conference, id=conference_id)
    author=Author.objects.get(user=request.user ,conferences=conference) # added the conferences=conference (22/6/24 11:02)
    is_registered = registered_authors.objects.filter(author=author, conference=conference).exists()

    # is_author=Author.objects.filter(user=request.user,conferences=conference).exists()
    # if is_author:
    tracks= Track.objects.filter(conference_id=conference.id).all().values()
    papers=Paper.objects.filter(authors=author).all().values()
    paper_names=Paper.objects.filter(authors=author).all().values('id')
    if(is_registered):
      reviews_for_submittedpapers = Review.objects.filter(paper__in=paper_names)
    else:
      reviews_for_submittedpapers =None

    # for submitting paper 
    if request.method=="POST":
      if timezone.localtime(timezone.now()).date() > conference.submission_deadline:
           messages.info(request,"You can't submit now as the submission deadline is over. ")
           return redirect('/conference/'+str(conference_id)+'/author/')  
      else:
       title = request.POST['title']
       abstract = request.POST['abstract']
       file = request.FILES['paper']
       conf = conference
       track = get_object_or_404(Track,title=request.POST["track"])
       authors = get_object_or_404(Author,user=request.user ,conferences =conference)
       status = 'submitted'
       keywords= request.POST['keywords']
       submissionDate= timezone.now().date() 
       otherauthors=request.POST['other-authors']


       print(otherauthors) 
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
       subject = 'New paper submitted.'
       message = f'Respected Program Chair,'\
                 f'\nNew paper '+str(paper.papertitle)+' has been submitted by the author '+str(paper.authors.user.first_name)+' '+str(paper.authors.user.last_name)+'.\n\nThank you'
       email_from = settings.EMAIL_HOST_USER
       recipient_list = [conference.programChair]
       send_mail(subject, message, email_from, recipient_list)

       messages.info(request,"Paper submitted succesfully.")
       
       return redirect('/conference/'+str(conference_id)+'/author/')
    
    return render(request, 'authrs-view.html',context={"conference":conference,"tracks":tracks,"uploadedpapers":papers,"reviews":reviews_for_submittedpapers,"is_registered":is_registered})
    # else:
    #     # The user is not an author for this conference
    #      return HttpResponseForbidden("You are not authorized as an author in this conference. To join as author select 'join as author' on the conference main page.")

@login_required
def unsubmitPaper(request,paper_id,conference_id):
  paper = get_object_or_404(Paper,id=paper_id)
  subject = 'Paper deleted by an author.'
  message1 = 'Respected Program Chair,'+'\nPaper submitted by '+str(paper.authors.user.first_name)+' '+str(paper.authors.user.last_name)+' on '+str(paper.submissionDate)+', was deleted today by the author.''\n\nThankyou'
  message2 = 'Respected Reviewer,'+'\nPaper which was to be reviewed - '+str(paper.papertitle)+' was deleted today by the author.''\n\nThankyou'
  email_from = settings.EMAIL_HOST_USER
  recipient_list1 = [paper.conference.programChair ]
  recipient_list2 = [paper.reviewers ]
  paper.delete()
  send_mail( subject, message1, email_from, recipient_list1 )
  send_mail(subject,message2,email_from,recipient_list2)
  messages.info(request,"Paper unsubmitted.")
  return redirect('/conference/'+str(conference_id)+'/author/')

@login_required
def resubmit_paper(request, conference_id,paper_id):
    conference=get_object_or_404(Conference,id=conference_id)
    paper = get_object_or_404(Paper, id=paper_id)

    if request.method == 'POST': 
        abstract = request.POST.get('abstract')
        file = request.FILES.get('paper')

        if  abstract and file:
            paper.abstract = abstract
            paper.file = file

            # Set status back to "submitted"
            paper.status = 'submitted'

            # Save and redirect
            paper.save()
            subject = 'New paper submitted.'
            message = f'Respected Program Chair,'\
                      f'\nPaper '+str(paper.papertitle)+' has been resubmitted by the author '+str(paper.authors.user.first_name)+' '+str(paper.authors.user.last_name)+'.\n\nThank you'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [conference.programChair]
            send_mail(subject, message, email_from, recipient_list)
            messages.info(request,"Paper resubmitted succesfully.")
       
            return redirect('/conference/'+str(conference_id)+'/author/')  
        else:
            return HttpResponseForbidden("Invalid form submission.")

    return redirect('/conference/'+str(conference_id)+'/author/') 

#  views for reviewer   
@login_required
def reviewer(request,conference_id):
    print(request.user)
    conference = get_object_or_404(Conference, id=conference_id)
    reviewer=Reviewer.objects.get(user=request.user , conference =conference)
    papers = Paper.objects.filter(reviewers=reviewer, conference=conference).exclude(review__reviewer=reviewer)
    reviews=Review.objects.filter(reviewer=reviewer)
    context={"conference":conference,"papers":papers,"reviews":reviews}
    return render(request, 'reviewer-view.html',context)

@login_required
def submitreview(request,conference_id,paper_id):
    paper=Paper.objects.get(id=paper_id) 
    conference = get_object_or_404(Conference, id=conference_id)
    reviewer=Reviewer.objects.get(user=request.user , conference =conference)
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

    if paper.has_review():
     subject = 'New paper reviewed.'
     message1 = 'Respected Program Chair,'+'\nAll reviewers assigned to the paper '+str(paper.papertitle)+' submitted by Author - '+str(paper.authors.user.first_name)+' '+str(paper.authors.user.last_name)+' have reviewed it.\n\nThankyou'
     message2 = 'Respected Author,'+'\n Your paper'+str(paper.papertitle)+' has been reviewed.\n\nThankyou'
     email_from = settings.EMAIL_HOST_USER
     recipient_list1 = [paper.conference.programChair ]
     recipient_list2 = [paper.authors ]
     send_mail( subject, message1, email_from, recipient_list1 )
     send_mail(subject,message2,email_from,recipient_list2)
    messages.info(request,"Review submitted.")
    return redirect('/conference/' + str(conference_id) + '/reviewer/')


# show the submitted papers by the authors 

def displaypdf(request,paper_id,conference_id):
   conference = Conference.objects.get( id=conference_id)
   paper=Paper.objects.get(id=paper_id)
   path=paper.file.url
   txt=path.split('/',1)
   pdf_file=txt[1]                # note : here for local host this path is valid it may change for different server where you upload so change accordingly 
   file_name, file_extension = os.path.splitext(paper.file.url)
   if(file_extension=='.pdf'):
       with open(pdf_file, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename=mypdf.pdf'
            return response
   else:
        context={"paper":paper,"conference":conference,"file":pdf_file}
        print(context)
        return render(request,'display.html',context)




@login_required
def deletePaper(request, paper_id, conference_id):
    conference = Conference.objects.get( id=conference_id)
    paper = get_object_or_404(Paper, id=paper_id)
    author=paper.authors
    # Check if the user is the program chair for the conference
    if not conference.is_chair(request.user):
        return HttpResponseForbidden("You are not authorized to assign reviewers to this paper.")
    
    # delete the paper 
    paper.delete()

    # mail to the author
    subject = 'Notification For Deleting your Paper.'
    message = f'Respected {author.user.first_name} {author.user.last_name},'\
            f'\nYour paper {paper.papertitle} from conference {conference.conferenceTitle} has been deleted successfully as requested .\n\nThank you'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [author.user.email]
    send_mail(subject, message, email_from, recipient_list)

    messages.info(request, "Paper deleted successfully, and notifying emails have been sent.")
    return redirect('/conference/' + str(conference.id) + '/programChair/') 

