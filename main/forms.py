# main/forms.py
from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 rounded-lg bg-slate-100 border-none', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-3 rounded-lg bg-slate-100 border-none', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'w-full p-3 rounded-lg bg-slate-100 border-none', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'w-full p-3 rounded-lg bg-slate-100 border-none', 'placeholder': 'Your Message', 'rows': 4}),
        }