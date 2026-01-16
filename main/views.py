import os, json, time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse, StreamingHttpResponse
from google import genai
from .models import Project, Skill, Profile, Experience, ChatLog, OtherLinks, Education, Certification
from .forms import ContactForm
from django_ratelimit.decorators import ratelimit

# ---------------------------------------------------
# VIEW FUNCTIONS
# ---------------------------------------------------

def portfolio_view(request):
    projects = Project.objects.all().order_by("-created_at")
    all_skills = Skill.objects.all()
    profile = Profile.objects.first()
    experiences = Experience.objects.all()
    otherLinks = OtherLinks.objects.all()
    education = Education.objects.all().order_by("-admissionYear")
    certificates = Certification.objects.all().order_by("-year")

    if not profile:
        return render(request, 'main/portfolio.html', {'error': 'Please add a profile in admin'})
    
    categories = [choice[0] for choice in Skill.CATEGORY_CHOICES]
    grouped_skills = {
        cat: all_skills.filter(category=cat) 
        for cat in categories if all_skills.filter(category=cat).exists()
    }

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            instance = form.save()
            
            email_context = {
                'flow': "New Portfolio Inquiry",
                'name': instance.name,
                'email': instance.email,
                'subject': instance.subject,
                'message': instance.message,
            }

            html_message = render_to_string('main/email_template.html', email_context)
            email = EmailMessage(
                subject=f"Inquiry: {instance.subject}",
                body=html_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.EMAIL_HOST_USER],
            )
            email.content_subtype = "html"
            email.send()

            email_to_user = {
                'flow': "Message Received!",
                'name': profile.fname,
                'email': profile.email,
                'subject': "Confirmation for Message received",
                'message': "I have received your message and will get back to you soon",
            }
            html_email_to_user = render_to_string('main/email_template.html', email_to_user)
            reply = EmailMessage(
                subject="Thanks for reaching out!",
                body=html_email_to_user,
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.email],
            )
            reply.content_subtype = "html"
            reply.send()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Your message has been sent successfully! ✅'})
            
            messages.success(request, "Your message has been sent successfully! ✅")
            return redirect('portfolio')
    else:
        form = ContactForm()

    full_name = f"{profile.fname} {profile.mname or ''} {profile.lname}".strip().replace('  ', ' ')
    
    context = {
        'profile': profile,
        'projects': projects,
        'grouped_skills': grouped_skills,
        'experiences': experiences,
        'form': form,
        'name': full_name,
        'education':education,
        'certificates':certificates,
        'otherLinks': otherLinks
    }
    return render(request, 'main/portfolio.html', context)

# ---------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------

def get_genai_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return genai.Client(api_key=api_key)

def get_fallback_models(client):
    try:
        available_models = client.models.list()
        flash_models = [
            m.name for m in available_models 
            if 'flash' in m.name.lower() and 'generateContent' in m.supported_actions
        ]
        if flash_models:
            return sorted(flash_models, reverse=True)
        return ["models/gemini-2.0-flash", "models/gemini-1.5-flash"]
    except Exception as e:
        print(f"Discovery Error: {e}")
        return ["models/gemini-2.0-flash", "models/gemini-1.5-flash"]

# ---------------------------------------------------
# CHATBOT VIEW
# ---------------------------------------------------

@ratelimit(key='ip', rate='10/m', block=True)
def ai_chatBot(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
    user_query = request.POST.get("message")
    profile = Profile.objects.first()
    if not profile:
        return JsonResponse({'status': 'error', 'message': 'Profile missing'})

    # 1. Session and History Management
    if not request.session.session_key:
        request.session.create()

    chat_history = request.session.get('chat_history', [])
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]

    history_context = ""
    for msg in chat_history:
        role = "User" if msg['role'] == 'user' else "Assistant"
        history_context += f"{role}: {msg['content']}\n"

    # 2. RAG Retrieval
    skills = Skill.objects.all()
    experience = Experience.objects.all()
    projects = Project.objects.all()
    links = OtherLinks.objects.all()
    education = Education.objects.all()
    certs = Certification.objects.all()

    # 3. Prompt Construction
    full_name = f"{profile.fname} {profile.mname or ''} {profile.lname}".strip().replace('  ', ' ')
    prompt_context = f"Name: {full_name}. Profession: {profile.profession}. Bio: {profile.objective}. "
    prompt_context += "Skills: " + ", ".join([s.name for s in skills]) + ". "
    prompt_context += "Experience: " + " | ".join([f"{e.role} at {e.company}: {e.description}" for e in experience])
    prompt_context += " Projects: " + " | ".join([f"{p.title} ({p.technologies}): {p.description}" for p in projects])
    prompt_context += f" Contact: Email: {profile.email}. Phone: {profile.phone}. " 
    prompt_context += "Education: " + " | ".join([f"{e.courseName} from {e.college} (CGPA/%: {e.CGPA})" for e in education]) + ". "
    prompt_context += "Certifications: " + ", ".join([c.courseName for c in certs]) + ". "
    prompt_context += "Profiles/Links: " + ", ".join([f"{l.name}: {l.link}" for l in links])

    system_instruction = f"""
    You are the professional AI Career Assistant for {profile.fname}. 
    Your mission: Briefly and professionally help recruiters understand {profile.fname}'s value.

    STRICT OPERATIONAL RULES:
    Tone: Professional, helpful, and concise.
    1. GROUNDING: Answer ONLY using the provided context. If information is missing, say: "I can only provide professional information about {profile.fname}. Please contact him directly for details on this."
    2. BREVITY: Keep answers concise (approx 30 words).
    3. FORMATTING: Use **Bold** for tech/degrees. Use single dash (-) for bullets.
    4. CONTACT: Provide email and phone clearly if asked.
    5. if they GREET: Greet users back politely.
    # Change these rules in your system_instruction:
    6. NO GREETINGS: Do not say "Hello," "Hi," or "Greetings." in every message.( avaoid if you have greeted earlier until they greets or says thank you)
    7. DIRECT ANSWERS: Start the response immediately with the information requested.
    CONVERSATION HISTORY:
    8. If reqruiter ask for " Are you available for hire?" response postively and convence them that {profile.fname} is the Quick leaner ready to adap whatever skills required please lets connect also provde contact details if requored.
    {history_context}

    CONTEXT:
    {prompt_context}
    """

    final_model_used = "Discovery Failed"

    # 4. Response Streaming Generator
    def stream_response():
        nonlocal final_model_used
        client = get_genai_client()
        model_queue = get_fallback_models(client)

        full_response_text = ""
        success = False

        for model_id in model_queue:
            try: 
                print(f"DEBUG: Attempting to stream from {model_id}")
                response = client.models.generate_content_stream(
                    model=model_id,
                    contents=f"{system_instruction}\n\n User Question: {user_query}",
                )
                has_chunks = False
                for chunk in response:
                    if chunk.text:
                        has_chunks = True
                        chunk_text = chunk.text
                        full_response_text += chunk_text
                        yield f"data: {json.dumps({'text': chunk_text})}\n\n"

                
                if has_chunks:
                    final_model_used = model_id
                    success = True
                    break
            except Exception as e:
                print(f"DEBUG ERROR with {model_id}: {e}") # This will show in your terminal
                continue

        if success:
            ChatLog.objects.create(
                user_query=user_query,
                ai_response=full_response_text,
                model_used=final_model_used,
                session_key=request.session.session_key
            )

            chat_history.append({'role': 'user', 'content': user_query})
            chat_history.append({'role': 'assistant', 'content': full_response_text})
            request.session['chat_history'] = chat_history
            request.session.modified = True

    # 5. Return the Stream (Corrected Indentation)
    response = StreamingHttpResponse(stream_response(), content_type='text/event-stream') 
    response['Cache-Control'] = 'no-cache'
    return response