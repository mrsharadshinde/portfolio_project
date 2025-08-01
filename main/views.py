from django.shortcuts import render

# main/views.py

from .models import Project, Skill

def portfolio_view(request):
    projects = Project.objects.all()
    skills = Skill.objects.all()
    
    # Your personal details
    context = {
        'name': 'Sharad Mahadev Shinde',
        'email': 'shindesharad9325@gmail.com',
        'phone': '9325262651',
        'github': 'https://github.com/mrsharadshinde',
        'linkedin': 'https://linkedin.com/in/mrsharadshinde',
        'objective': 'Detail-oriented MCA student specializing in database management and SQL. Proven experience in designing and implementing relational databases for full-stack applications using MySQL and Python. Eager to apply my skills in data querying, schema design, and problem-solving to an SQL Developer or Python developer Role', # You can copy the full objective here
        'projects': projects,
        'skills': skills,
    }
    return render(request, 'main/portfolio.html', context)
