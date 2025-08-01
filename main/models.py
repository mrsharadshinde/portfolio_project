# main/models.py
from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.CharField(max_length=200)
    link = models.URLField(blank=True, null=True)


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
    # proficiency = models.IntegerField(default=80) # Optional: You can add this back if you want a proficiency bar

    def __str__(self):
        return self.name