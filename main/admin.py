from django.contrib import admin
from .models import Project, Skill, Profile, Experience,Education,OtherLinks, ContactMessage, ChatLog,  Certification
# Register your models here.
admin.site.register(Project)
admin.site.register(Skill)
admin.site.register(Profile)
admin.site.register(Experience)
admin.site.register(OtherLinks)
admin.site.register(Education)
admin.site.register(Certification)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    readonly_fields = ('name', 'email', 'subject', 'created_at', 'message')

@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_query', 'model_used')
    readonly_fields = ('timestamp', 'user_query', 'ai_response','model_used','session_key')
    search_fields = ('user_query', 'ai_response')