from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator,MaxValueValidator
from django.utils import timezone

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, phone, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        if not phone:
            raise ValueError('The given phone must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, phone, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        if not email:
            raise ValueError("Email Required")
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, phone, password, **extra_fields)

    def create_superuser(self, email, phone, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, phone, password, **extra_fields)
    
# Create your models here.
class User(AbstractUser):
    """User model."""
    username=None
    formal_title=models.CharField(
        max_length=4
    )
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(blank=True)
    profession=models.CharField(max_length=50)
    afiliation=models.CharField(max_length=225,default=None,null=True)
    role=models.CharField(max_length=225,default=None,null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']
    
    def __str__(self):
        return self.email
    
class Conference(models.Model):
    conferenceTitle = models.CharField(max_length=255,unique=True)
    programChair = models.ForeignKey(User, on_delete=models.CASCADE)
    about_conference=models.TextField(null=True)
    organizing_institute = models.CharField(max_length=255)
    institute_details = models.TextField(null=True)
    submission_deadline = models.DateField()
    notification_of_acceptance = models.DateField()
    registration_deadline=models.DateField()
    camera_ready_papers=models.DateField()
    conference_date=models.DateField()
    conference_venue=models.CharField(max_length=225,null="True")

    def __str__(self):
        return self.conferenceTitle
    
    def submissions_open(self):
        return timezone.now().date() <= self.submission_deadline
    
    def is_chair(self, user):
        return user==self.programChair

class committeeImages(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    committee_image=models.FileField(upload_to='image/',null=True)

    def __str__(self):
        return self.conference.conferenceTitle
    
class conferenceImages(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    conference_image=models.FileField(upload_to='image/',null=True)

    def __str__(self):
        return self.conference.conferenceTitle
    
class Track(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    subDomains = models.TextField()
    
    class Meta:
        unique_together = ['conference', 'title']

    def __str__(self):
         return f"{self.title} - {self.conference.conferenceTitle}"

class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conferences = models.ManyToManyField(Conference)
    
    def __str__(self):
        return self.user.email

class registered_authors(models.Model):
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    conference=models.ForeignKey(Conference,on_delete=models.CASCADE)

    def __str__(self) :
        return f" {self.author.user.email} registered for {self.conference.conferenceTitle}"

class Reviewer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE,null="True")

    def __str__(self):
        return self.user.email

class Paper(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('Rejected due to Plagarism','Rejected due to Plagarism'),
        ('Desktop Rejected','Desktop Rejected')
    ]

    papertitle = models.CharField(max_length=255)
    abstract = models.TextField()
    file = models.FileField(upload_to='paper/')
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    authors = models.ForeignKey(Author, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='submitted')
    keywords=models.TextField()
    submissionDate=models.DateField()
    otherauthors=models.CharField(max_length=125,null=True)
    reviewers = models.ManyToManyField(Reviewer, related_name='papers', blank=True)
    

    def __str__(self):
         print("The value of papertitle is", str(self.papertitle))
         return self.papertitle
    
    def is_author(self, user):
        return self.authors.filter(user=user).exists()
    
    def is_reviewer(self, user):
        return self.reviewer.filter(user=user).exists()
    
    def has_review(self):
        assigned_reviewers_count = self.reviewers.count()
        submitted_reviews_count = Review.objects.filter(paper=self).count()

        return assigned_reviewers_count == submitted_reviews_count
    
class Review(models.Model):
    RESULT_CHOICES = [
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    relevance = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    writingStyle = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    reviewerConfidence = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    result=models.CharField(choices=RESULT_CHOICES,max_length=20,null=True)
    modeOfPreparation= models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
    comments = models.TextField()
    confidentialremarks=models.TextField(null=True)

    class Meta:
        unique_together = ['paper', 'reviewer']

    def __str__(self):
        return f"Review for {self.paper.papertitle} by {self.reviewer.user.email}"
    
