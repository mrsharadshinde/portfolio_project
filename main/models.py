# main/models.py
from django.db import models
import os
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class Profile(models.Model):
    fname = models.CharField(max_length=50, default="Your Fname")
    mname = models.CharField(max_length=50, default="Your Mname")
    lname = models.CharField(max_length=50, default="your Lname")
    
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    github = models.URLField()
    linkedin = models.URLField()
    objective = models.TextField()
    profession = models.CharField(max_length=200) # Added max_length here
    profile_image = models.ImageField(
        upload_to='profile/',
        default='profile/photo.jpg', 
        blank=True, 
        null=True
    )
    resume = models.FileField(upload_to ='resume/', blank=True, null=True)
    def __str__(self):
         return f"{self.fname} {self.lname}"

@receiver(pre_save, sender=Profile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem when change occurs.
    """
    if not instance.pk:
        return False

    try:
        # Fetch the old record from the database
        old_file = Profile.objects.get(pk=instance.pk).profile_image
    except Profile.DoesNotExist:
        return False

    new_file = instance.profile_image
    
    # If file is changed AND it's not the default image, delete the old physical file
    if old_file and not old_file == new_file and old_file.name != 'profile/photo.jpg':
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

   
class Project(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    technologies = models.CharField(max_length=200)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('Language', 'Programming Language'),
        ('Framework', 'Framework & Technology'),
        ('Database', 'Database'),
        ('Concept', 'Concept'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    icon_class = models.CharField(
        max_length=100, 
        default='fas fa-code', 
        help_text="Font Awesome class, e.g., 'fab fa-python'"
    )
    # proficiency = models.IntegerField(default=80) # Optional: You can add this back if you want a proficiency bar

    def __str__(self):
        return self.name

class Experience(models.Model):
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    duration = models.CharField(max_length=200)
    description = models.TextField()
    is_currunt = models.BooleanField(default= False)
    created_at = models.DateTimeField(auto_now_add=True)

    class meta:
        ordering = ['-created_at'] #shows the new at top

    def __str__(self):
        return f"{self.role} at {self.company}"
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

class OtherLinks(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField()

    def __str__(self):
        return self.name

class Education(models.Model):
    courseName = models.CharField(max_length=300)
    admissionYear = models.DateField()
    passingYear = models.DateField()
    college = models.CharField(max_length=300)
    CGPA = models.CharField(max_length=50)
   
    def clean(self):
        if self.admissionYear and self.passingYear:
            if self.admissionYear > self.passingYear:
                raise ValidationError({
                    'passingYear': 'Passing year must be greater than admission year.'
                })
            
    def save(self, *args, **kwargs):
        self.full_clean()          # ← THIS triggers clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.courseName
    
    #- ----------- validate input file 
def validate_certificate_file(value):
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.webp']
    if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError("Only PDF and image files are allowed.")
    
class Certification(models.Model):
    courseName = models.CharField(max_length=300)
    year = models.DateField(max_length=50)
    certificate = models.FileField(
        upload_to='certificates/',
        validators=[validate_certificate_file]
    )
    thumbnail = models.ImageField(upload_to='certificates/thumbnails/', blank=True, null= True)
    credential_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.courseName

class ChatLog(models.Model):
    user_query = models.TextField()
    ai_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    model_used = models.CharField(max_length=100, blank=True, null=True)
    session_key = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Query at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"