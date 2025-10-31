from django.shortcuts import  render, redirect, get_object_or_404
from django.conf import settings 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
import random
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import ContactModel, ClientReview, Client_Logo, Technologies, Blog, Team, ProjectModel, Certificates, Category, Website, Service, Career_Model, Candidate
from .forms import ContactModelForm, ClientReviewForm, Client_Logo_Form, TechnologiesForm, BlogForm, TeamForm, ProjectModelForm, CertificatesForm, CategoryForm, WebsiteForm, CareerForm, CandidateForm

from .models import Services

def service_api_detail(request, pk):
    service = get_object_or_404(Services, pk=pk)
    
    data = {
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'image': service.image.url if service.image else None,
        'offers': [
            {
                'id': offer.id,
                'title': offer.title,
                'description': offer.description
            } for offer in service.offers.all()
        ],
        'steps': [
            {
                'id': step.id,
                'title': step.title,
                'tagline': step.tagline
            } for step in service.process_steps.all()
        ],
        'faqs': [
            {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer
            } for faq in service.faqs.all()
        ]
    }
    
    return JsonResponse(data)


# def services(request):
#     services = Services.objects.prefetch_related("offers").all()
#     other_services = Services.objects.exclude(id__in=services.values_list('id', flat=True))[:7]
#     context={
#         'services':services,
#         'other_services':other_services
#     }
#     return render(request, 'home/service.html',context)

def service_detail(request, id):
    service = get_object_or_404(Services, id=id)
    services = Services.objects.all()   
    offers = getattr(service, 'offers', None)  # if offers is a related_name
    other_services = Services.objects.exclude(id=service.id)[:7]
    process_steps = service.process_steps.all().order_by('id')
    
    context = {
        'service': service,
        'offers': offers,
        'other_services': other_services,
        'process_steps': process_steps,
        'services':services
    }
    return render(request, 'home/service.html', context)


from .models import Services
from .forms import ServiceForm, OfferFormSet, StepFormSet,FAQFormSet

def service_list(request):
    services = Services.objects.all()
    return render(request, "admin_home/service_list.html", {"services": services})


def service_create(request):
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)
        offer_formset = OfferFormSet(request.POST)
        step_formset = StepFormSet(request.POST)
        faq_formset = FAQFormSet(request.POST)

        if (form.is_valid() and offer_formset.is_valid() and
            step_formset.is_valid() and faq_formset.is_valid()):

            service = form.save()
            offer_formset.instance = service
            step_formset.instance = service
            faq_formset.instance = service

            offer_formset.save()
            step_formset.save()
            faq_formset.save()

            messages.success(request, "Service created successfully.")
            return redirect("service_list")
    else:
        form = ServiceForm()
        offer_formset = OfferFormSet()
        step_formset = StepFormSet()
        faq_formset = FAQFormSet()

    return render(request, "admin_home/add_service.html", {
        "form": form,
        "offer_formset": offer_formset,
        "step_formset": step_formset,
        "faq_formset": faq_formset,
        "title": "Add Service"
    })

from .models import *

def service_update(request, pk):
    service = get_object_or_404(Services, pk=pk)
    
    if request.method == "POST":
        try:
            # Handle main service form
            form = ServiceForm(request.POST, request.FILES, instance=service)
            
            if form.is_valid():
                # Save the main service first
                service = form.save()
                
                # Handle offers
                offer_count = int(request.POST.get('offers-TOTAL_FORMS', 0))
                print(f"Processing {offer_count} offers")
                
                for i in range(offer_count):
                    offer_id = request.POST.get(f'offers-{i}-id', '')
                    title = request.POST.get(f'offers-{i}-title', '').strip()
                    description = request.POST.get(f'offers-{i}-description', '').strip()
                    should_delete = request.POST.get(f'offers-{i}-DELETE') == 'on'
                    
                    print(f"Offer {i}: id={offer_id}, title='{title}', delete={should_delete}")
                    
                    if offer_id and offer_id != '':
                        # Existing offer
                        try:
                            offer = ServiceOffer.objects.get(id=int(offer_id), service=service)
                            if should_delete:
                                print(f"Deleting offer {offer_id}")
                                offer.delete()
                            elif title and description:
                                print(f"Updating offer {offer_id}")
                                offer.title = title
                                offer.description = description
                                offer.save()
                            else:
                                # If fields are empty, delete the offer
                                print(f"Deleting empty offer {offer_id}")
                                offer.delete()
                        except ServiceOffer.DoesNotExist:
                            print(f"Offer {offer_id} not found")
                            pass
                    elif title and description and not should_delete:
                        # New offer
                        print(f"Creating new offer: {title}")
                        ServiceOffer.objects.create(
                            service=service,
                            title=title,
                            description=description
                        )
                
                # Handle process steps - MUST HAVE EXACTLY 4
                step_count = int(request.POST.get('steps-TOTAL_FORMS', 0))
                print(f"Processing {step_count} steps")
                
                for i in range(step_count):
                    step_id = request.POST.get(f'steps-{i}-id', '')
                    title = request.POST.get(f'steps-{i}-title', '').strip()
                    tagline = request.POST.get(f'steps-{i}-tagline', '').strip()
                    
                    print(f"Step {i}: id={step_id}, title='{title}'")
                    
                    if step_id and step_id != '':
                        # Existing step - update only
                        try:
                            step = ServiceProcessStep.objects.get(id=int(step_id), service=service)
                            if title and tagline:
                                print(f"Updating step {step_id}")
                                step.title = title
                                step.tagline = tagline
                                step.save()
                        except ServiceProcessStep.DoesNotExist:
                            print(f"Step {step_id} not found")
                            pass
                    elif title and tagline:
                        # New step
                        print(f"Creating new step: {title}")
                        ServiceProcessStep.objects.create(
                            service=service,
                            title=title,
                            tagline=tagline
                        )
                
                # Handle FAQs
                faq_count = int(request.POST.get('faqs-TOTAL_FORMS', 0))
                print(f"Processing {faq_count} FAQs")
                
                for i in range(faq_count):
                    faq_id = request.POST.get(f'faqs-{i}-id', '')
                    question = request.POST.get(f'faqs-{i}-question', '').strip()
                    answer = request.POST.get(f'faqs-{i}-answer', '').strip()
                    should_delete = request.POST.get(f'faqs-{i}-DELETE') == 'on'
                    
                    print(f"FAQ {i}: id={faq_id}, question='{question}', delete={should_delete}")
                    
                    if faq_id and faq_id != '':
                        # Existing FAQ
                        try:
                            faq = ServiceFAQ.objects.get(id=int(faq_id), service=service)
                            if should_delete:
                                print(f"Deleting FAQ {faq_id}")
                                faq.delete()
                            elif question and answer:
                                print(f"Updating FAQ {faq_id}")
                                faq.question = question
                                faq.answer = answer
                                faq.save()
                            else:
                                # If fields are empty, delete the FAQ
                                print(f"Deleting empty FAQ {faq_id}")
                                faq.delete()
                        except ServiceFAQ.DoesNotExist:
                            print(f"FAQ {faq_id} not found")
                            pass
                    elif question and answer and not should_delete:
                        # New FAQ
                        print(f"Creating new FAQ: {question}")
                        ServiceFAQ.objects.create(
                            service=service,
                            question=question,
                            answer=answer
                        )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Service updated successfully!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below.',
                    'errors': {'form': form.errors.get_json_data()}
                }, status=400)
                
        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'message': f'Error updating service: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)
        
        

def service_delete(request, pk):
    service = get_object_or_404(Services, pk=pk)
    service.delete()
    messages.success(request, "Service deleted successfully.")
    return redirect("service_list")










def index(request):
    technologies = Technologies.objects.all()
    # client_logos = Client_Logo.objects.all()
    reviews = ClientReview.objects.all() 
    # projects = list(ProjectModel.objects.all())  # Convert QuerySet to list
    # random.shuffle(projects)  # Shuffle the list
    # projects = projects[:6] 
    cat = Category.objects.all()
    projects = ProjectModel.objects.all()
    blogs = Blog.objects.all()
    services = Services.objects.all()   
    active_banner = PromotionalBanner.objects.filter(
        status='active',
        end_date__gte=timezone.now()
    ).first()
    
    

    # if request.method == 'POST':
    #     id1 = request.POST.get('id1')
    #     pdf_url = generate_certificate_url(id1)
    #     if pdf_url:
    #         messages.success(request, "Your certificate has been successfully generated!")
    #         return render(request, 'certificate.html', {'pdf_url': pdf_url})
    #     else:
    #         messages.error(request, "Oops! No certificate found for the provided ID. Please try again.")
    #         return redirect('index')
    # return render(request, 'index.html',{ 'client_logos' : client_logos, 'reviews':reviews,'projects': projects})
    return render(request, 'home/index.html',{'active_banner': active_banner,'cat':cat,'technologies': technologies,'projects':projects,'reviews':reviews,'blogs':blogs,'services':services})

def index_redirect(request):
    return redirect('index')

def generate_certificate_url(id):
    try:
        certificate = Certificates.objects.get(id1=id)
        return f'{settings.MEDIA_URL}{certificate.pdf_file}'
    except Certificates.DoesNotExist:
        return None

def about(request):
    # technologies = Technologies.objects.all()
    client_logos = Client_Logo.objects.all()
    services = Services.objects.all()   
    # team_members = Team.objects.all()
    # if request.method == 'POST':
    #     id1 = request.POST.get('id1')
    #     pdf_url = generate_certificate_url(id1)
    #     if pdf_url:
    #         return render(request, 'certificate.html', {'pdf_url': pdf_url})
    #     else:
    #         messages.error(request, ("Certificate not found for the provided ID!!!"))
    #         return redirect('about')
    # return render(request, 'about.html',{'technologies': technologies, 'client_logos' : client_logos, 'team_members':team_members})
    return render(request,'home/about.html',{'client_logos': client_logos,'services':services})

# def contact(request):
#     if request.method == 'POST':
#         form = ContactModelForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Your message has been successfully submitted.')
#             return redirect('contact')
#         else:
#             messages.error(request, "Oops! Please try again.")
#             return redirect('contact')
#     else:
#         form = ContactModelForm()
#     return render(request, 'home/contact.html', {'form': form})

def contact(request):
    services = Services.objects.all()   
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ContactModelForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ContactModelForm()
    return render(request, 'home/contact.html', {'form': form,'services':services})

def portfolio(request):
    projects = ProjectModel.objects.all()
    services = Services.objects.all()   
    # return render(request,'portfolio.html', {'projects':projects})
    return render(request,'home/works.html',{'projects':projects,'services':services})


def advertising(request):
    return render(request, 'advertising.html')

def web_development(request):
    return render(request, 'web_development.html')

def digital_marketing(request):
    return render(request, 'digital_marketing.html')

def trademark(request):
    return render(request, 'trademark.html')

def branding(request):
    return render(request, 'branding.html')

def it_solutions(request):
    return render(request, 'it_solutions.html')

def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')

def privacy_and_policy(request):
    return render(request, 'privacy_and_policy.html')




def career_submit_application(request):
    # Get active job positions
    job_positions = Career_Model.objects.filter(post_end_date__gte=timezone.now())
    careers = Career_Model.objects.filter(post_end_date__gte=timezone.now())
    services = Services.objects.all()   
    
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your application has been successfully submitted.')
            return redirect('submit_application')  # Make sure 'careers' is a valid URL name
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CandidateForm()

    context = {
        'form': form,
        'job_positions': job_positions,
        'careers': careers,
        'services':services
    }
    return render(request, 'home/careers.html', context)


    
# def career_submit_application(request):
#     job_positions = Career_Model.objects.filter(is_active=True)  # optional: only active jobs

#     if request.method == 'POST':
#         form = CandidateForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Your application has been successfully submitted.')
#             return redirect('careers')
#         messages.error(request, 'Please correct the errors below.')
#     else:
#         form = CandidateForm()

#     context = {
#         'form': form,
#         'job_positions': job_positions
#     }
#     return render(request, 'home/careers.html', context)

# def career_submit_application(request):
#     candidate_form = CandidateForm()
#     job_positions = Career_Model.objects.all()
#     if request.method == 'POST':
#         form = CandidateForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Your application has been successfully submitted.')
#             return redirect('careers')  # Redirect after successful submission
#         else:
#             messages.error(request, "Oops! Please try again.")
#             return redirect('careers')
#     else:
#         form = CandidateForm()

#     return render(request, 'home/careers.html', {'form': form, 'job_positions':job_positions,'candidate_form': candidate_form})



    
    
    
# def submit_application(request):
#     job_positions = Career_Model.objects.all()
#     if request.method == 'POST':
#         form = CandidateForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Your application has been successfully submitted.')
#             return redirect('careers')  # Redirect after successful submission
#         else:
#             messages.error(request, "Oops! Please try again.")
#             return redirect('careers')
#     else:
#         form = CandidateForm()

#     return render(request, 'careers.html', {'form': form, 'job_positions':job_positions})


def blog(request):
    # blogs = Blog.objects.all().order_by('-created_date')
    # return render(request, 'blog.html', {'blogs': blogs})
    blogs = Blog.objects.all().order_by('-created_date')
    return render(request,'home/blog.html',{'blogs':blogs})


def blog_details(request, slug):  
    blog = get_object_or_404(Blog, slug=slug)  # Get blog by slug
    recent_posts = Blog.objects.exclude(id=blog.id).order_by('-created_date')[:4]  # Use blog.id instead of blog_id
    return render(request, 'home/blog_details.html', {'blog': blog,'recent_posts':recent_posts})


# Admin Side
@csrf_protect
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, Admin!")
            return redirect('dashboard')
        else:   
            messages.error(request, "There was an error logging in, try again.")
            return redirect('user_login')
    return render(request, 'home/login.html')


def logout_user(request):
    logout(request)
    messages.success(request, ("You Were Logged Out"))
    return redirect('user_login')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from .models import (
    ProjectModel, Team, Technologies, Blog, Certificates, ClientReview,
    ContactModel, Website, Career_Model, Candidate
)

@login_required(login_url='user_login')
def dashboard(request):
    # Counts
    active_projects_count = ProjectModel.objects.count()
    team_members_count = Team.objects.count()
    total_technologies = Technologies.objects.count()
    total_applications = Candidate.objects.count()
    pending_applications = Candidate.objects.filter(job_position__end_date__gte=timezone.now()).count()
    websites_built = Website.objects.count()
    certifications_count = Certificates.objects.count()
    blog_posts_count = Blog.objects.count()
    client_reviews_count = ClientReview.objects.count()

    # Project chart data (monthly completed projects)
    # Simple example: count projects by month of created_date
    from django.db.models.functions import TruncMonth
    from django.db.models import Count

    projects_by_month = (
    ProjectModel.objects
    .annotate(month=TruncMonth('created_date'))  # <-- Use created_date instead of id
    .values('month')
    .annotate(count=Count('id'))
    .order_by('month') )
    labels = [p['month'].strftime('%b %Y') if p['month'] else "Unknown" for p in projects_by_month]
    data = [p['count'] for p in projects_by_month]
    project_chart_data = {"labels": labels, "data": data}

    # Average rating for client satisfaction
    reviews = ClientReview.objects.all()
    average_rating = round(sum([5 for r in reviews]) / len(reviews), 1) if reviews else 0  # You can store numeric rating field
    satisfaction_offset = 283 - (average_rating / 5 * 283)

    # Rating stats (fake example, you can calculate based on actual numeric rating field)
    rating_stats = [
        {'stars': 5, 'bar_class': 'bg-success', 'percent': 60},
        {'stars': 4, 'bar_class': 'bg-info', 'percent': 25},
        {'stars': 3, 'bar_class': 'bg-warning', 'percent': 10},
        {'stars': 2, 'bar_class': 'bg-danger', 'percent': 3},
        {'stars': 1, 'bar_class': 'bg-dark', 'percent': 2},
    ]

    # Recent Activities (from Projects, Teams, Blogs)
    recent_activities = []

    for p in ProjectModel.objects.order_by('-id')[:5]:
        recent_activities.append({
            'title': f"Project Added: {p.project_name}",
            'description': getattr(p, 'project_name', 'No description'),
            'icon': "mdi mdi-briefcase-outline",
            'status_class': "primary",
            'time_ago': "Recently"
        })

    for t in Team.objects.order_by('-id')[:3]:
        recent_activities.append({
            'title': f"Team Member Added: {t.client_name}",
            'description': getattr(t, 'designation', ''),
            'icon': "mdi mdi-account-multiple",
            'status_class': "success",
            'time_ago': "Recently"
        })

    for b in Blog.objects.order_by('-id')[:3]:
        recent_activities.append({
            'title': f"Blog Published: {b.name}",
            'description': b.description[:80],
            'icon': "mdi mdi-post",
            'status_class': "warning",
            'time_ago': "Recently"
        })

    context = {
        "active_projects_count": active_projects_count,
        "team_members_count": team_members_count,
        "total_technologies": total_technologies,
        "total_applications": total_applications,
        "pending_applications": pending_applications,
        "websites_built": websites_built,
        "certifications_count": certifications_count,
        "blog_posts_count": blog_posts_count,
        "client_reviews_count": client_reviews_count,
        "project_chart_data": project_chart_data,
        "selected_period": "Last 6 Months",
        "average_rating": average_rating,
        "satisfaction_offset": satisfaction_offset,
        "rating_stats": rating_stats,
        "recent_activities": recent_activities,
    }

    return render(request, "admin_home/index.html", context)


# Contact 
@login_required(login_url='user_login')
def contact_view(request):
    contacts = ContactModel.objects.all().order_by('-id')  
    return render(request,'admin_home/contact_view.html',{'contacts':contacts})


@login_required(login_url='user_login')
def delete_contact(request,id):
    contact = ContactModel.objects.get(id=id)
    contact.delete()
    return redirect('contact_view')


# Client Reviews
@login_required(login_url='user_login')
def add_client_review(request):
    if request.method == 'POST':
        form = ClientReviewForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client review added successfully!')
            return redirect('view_client_reviews')
        else:
            messages.error(request, 'Error adding client review. please try again.')
    else:
        form = ClientReviewForm()

    return render(request, 'admin_home/add_client_review.html', {'form': form})


@login_required(login_url='user_login')
def view_client_reviews(request):
    client_reviews = ClientReview.objects.all().order_by('-id')
    return render(request, 'admin_home/view_client_reviews.html', {'client_reviews': client_reviews})


@login_required(login_url='user_login')
def update_client_review(request, id):
    client_reviews = get_object_or_404(ClientReview, id=id)
    if request.method == 'POST':
        form = ClientReviewForm(request.POST, request.FILES, instance=client_reviews)
        if form.is_valid():
            form.save()
            return redirect('view_client_reviews')
    else:
        form = ClientReviewForm(instance=client_reviews)
    return render(request, 'admin_pages/update_client_review.html', {'form': form, 'client_reviews': client_reviews})

    

@login_required(login_url='user_login')
def delete_client_review(request,id):
    client_reviews = ClientReview.objects.get(id=id)
    client_reviews.delete()
    return redirect('view_client_reviews')


#  Client Logo
@login_required(login_url='user_login')
def add_clients_logo(request):
    if request.method == 'POST':
        form = Client_Logo_Form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('view_clients_logo') 
    else:
        form = Client_Logo_Form()

    return render(request, 'admin_home/add_clients_logo.html', {'form': form})

@login_required(login_url='user_login')
def view_clients_logo(request):
    logo = Client_Logo.objects.all().order_by('-id')
    return render(request,'admin_home/view_clients_logo.html',{'logo':logo})

@login_required(login_url='user_login')
def update_clients_logo(request,id):
    logos = get_object_or_404(Client_Logo, id=id)
    if request.method == 'POST':
        form = Client_Logo_Form(request.POST, request.FILES, instance=logos)
        if form.is_valid():
            form.save()
            return redirect('view_clients_logo')
    else:
        form = Client_Logo_Form(instance=logos)
    return render(request, 'admin_pages/update_clients_logo.html', {'form': form, 'logos': logos})

@login_required(login_url='user_login')
def delete_clients_logo(request,id):
    logos = Client_Logo.objects.get(id=id)
    logos.delete()
    return redirect('view_clients_logo')



#  Technologies
@login_required(login_url='user_login')
def add_technologies(request):
    if request.method == 'POST':
        form = TechnologiesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('view_technologies') 
    else:
        form = Client_Logo_Form()

    return render(request, 'admin_home/add_technologies.html', {'form': form})

@login_required(login_url='user_login')
def view_technologies(request):
    logo = Technologies.objects.all().order_by('-id')
    return render(request,'admin_home/view_technologies.html',{'logo':logo})

@login_required(login_url='user_login')
def update_technologies(request,id):
    logos = get_object_or_404(Technologies, id=id)
    if request.method == 'POST':
        form = TechnologiesForm(request.POST, request.FILES, instance=logos)
        if form.is_valid():
            form.save()
            return redirect('view_technologies')
    else:
        form = TechnologiesForm(instance=logos)
    return render(request, 'admin_pages/update_technologies.html', {'form': form, 'logos': logos})

@login_required(login_url='user_login')
def delete_technologies(request,id):
    logos = Technologies.objects.get(id=id)
    logos.delete()
    return redirect('view_technologies')



@login_required(login_url='user_login')
def add_blog_details(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('view_blog_details') 
    else:
        form = BlogForm()

    return render(request, 'admin_home/add_blog_details.html', {'form': form})


@login_required(login_url='user_login')
def view_blog_details(request):
    blogs = Blog.objects.all().order_by('-id')
    return render(request, 'admin_home/view_blog_details.html', {'blogs': blogs})


@login_required(login_url='user_login')
def update_blog_details(request, id):
    blog = get_object_or_404(Blog, id=id)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('view_blog_details')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'admin_pages/update_blog_details.html', {'form': form, 'blog': blog})

@login_required(login_url='user_login')
def delete_blog_details(request,id):
    blogs = Blog.objects.get(id=id)
    blogs.delete()
    return redirect('view_blog_details')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

@csrf_exempt
def ckeditor_upload(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        upload = request.FILES['upload']
        file_extension = os.path.splitext(upload.name)[1].lower()
        
        # Check if the uploaded file is an image or a PDF
        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            folder = 'images'
        elif file_extension == '.pdf':
            folder = 'pdfs'
        else:
            return JsonResponse({'uploaded': False, 'error': 'Unsupported file type.'})

        # Save the file in the appropriate folder
        file_name = default_storage.save(f'{folder}/{upload.name}', ContentFile(upload.read()))
        file_url = default_storage.url(file_name)
        return JsonResponse({
            'uploaded': True,
            'url': file_url
        })
    
    return JsonResponse({'uploaded': False, 'error': 'No file was uploaded.'})


    
#Team
@login_required(login_url='user_login')
def add_team(request):
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('view_team') 
    else:
        form = TeamForm()

    return render(request, 'admin_home/add_team.html', {'form': form})


@login_required(login_url='user_login')
def view_team(request):
    client_reviews = Team.objects.all().order_by('-id')
    return render(request, 'admin_home/view_team.html', {'client_reviews': client_reviews})


@login_required(login_url='user_login')
def update_team(request, id):
    client_reviews = get_object_or_404(Team, id=id)
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES, instance=client_reviews)
        if form.is_valid():
            form.save()
            return redirect('view_team')
    else:
        form = TeamForm(instance=client_reviews)
    return render(request, 'admin_pages/update_team.html', {'form': form, 'client_reviews': client_reviews})

    

@login_required(login_url='user_login')
def delete_team(request,id):
    client_reviews = Team.objects.get(id=id)
    client_reviews.delete()
    return redirect('view_team')


def index_team(request):
    team_members = Team.objects.all()
    services = Services.objects.all()   
    return render(request, 'home/team.html', {'team_members': team_members,'services':services})
    


# def career(request):
#     careers = Career_Model.objects.all()
#     return render(request, 'home/careers.html',{'careers':careers})


#  404 view\
def page_404(request, exception):
    return render(request, '404.html', status=404)




# Portfolio 

@login_required(login_url='user_login')
def add_project(request):
    if request.method == 'POST':
        form = ProjectModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('view_projects')
        else:
            # Debug: show errors
            print(form.errors)  # For console debugging
    else:
        form = ProjectModelForm()

    return render(request, 'admin_home/add_project.html', {'form': form})


@login_required(login_url='user_login')
def view_projects(request):
    projects = ProjectModel.objects.all().order_by('-id')
    return render(request, 'admin_home/view_projects.html', {'projects': projects})

@login_required(login_url='user_login')
def update_projects(request, id):
    projects = get_object_or_404(ProjectModel, id=id)
    if request.method == 'POST':
        form = ProjectModelForm(request.POST, request.FILES, instance=projects)
        if form.is_valid():
            if 'remove_image' in request.POST:
                projects.project_image.delete() 
                projects.project_image = None 
            form.save()
            return redirect('view_projects')
    else:
        form = ProjectModelForm(instance=projects)
    return render(request, 'admin_pages/update_projects.html', {'form': form, 'projects': projects})

@login_required(login_url='user_login')
def delete_projects(request,id):
    projects = ProjectModel.objects.get(id=id)
    projects.delete()
    return redirect('view_projects')


# Certificate
@login_required(login_url='user_login')
def add_certificates(request):
    if request.method == 'POST':
        form = CertificatesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('view_certificates') 
    else:
        form = CertificatesForm()

    return render(request, 'admin_home/add_certificates.html', {'form': form})

@login_required(login_url='user_login')
def view_certificates(request):
    certificates = Certificates.objects.all().order_by('-id')
    return render(request, 'admin_home/view_certificates.html', {'certificates': certificates})


@login_required(login_url='user_login')
def update_certificates(request,id):
    certificates = get_object_or_404(Certificates, id=id)
    if request.method == 'POST':
        form = CertificatesForm(request.POST, request.FILES, instance=certificates)
        if form.is_valid():
            form.save()
            return redirect('view_certificates')
    else:
        form = CertificatesForm(instance=certificates)
    return render(request, 'admin_pages/update_certificates.html', {'form': form, 'certificates': certificates})


@login_required(login_url='user_login')
def delete_certificates(request,id):
    certificates = Certificates.objects.get(id=id)
    certificates.delete()
    return redirect('view_certificates')


def category_website_detail(request, category_slug, website_slug):
    category = get_object_or_404(Category, slug=category_slug)
    service = Services.objects.all()

    # Ensure the category slug is correct
    correct_slug = slugify(category.name)
    if category.slug != correct_slug:
        return redirect('website_detail', category_slug=correct_slug, website_slug=website_slug)

    # Fetch website correctly
    website = get_object_or_404(Website, slug=website_slug, category=category)

    # Retrieve related services
    faqs = website.faqs.all()
    services = Service.objects.filter(website=website)
    technologies = Technologies.objects.all()
    blogs = Blog.objects.all()
    testimonials = ClientReview.objects.all()

    return render(
        request,
        'home/website_detail.html',
        {'service':service,'category': category, 'website': website, 'faqs':faqs, 'services': services, 'technologies': technologies,'blogs':blogs,'testimonials':testimonials}
    )
   





# addd Catgeoory
@login_required(login_url='user_login')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('view_category') 
    else:
        form = CategoryForm()

    return render(request, 'admin_home/add_category.html', {'form': form})

@login_required(login_url='user_login')
def view_category(request):
    categories = Category.objects.all().order_by('-id')
    return render(request, "admin_home/view_category.html", {"categories": categories})




from django.utils.text import slugify

@login_required(login_url='user_login')
def update_category(request, id):
    category = get_object_or_404(Category, id=id)  # Fetch category by ID
    old_slug = category.slug  # Store old slug

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            updated_category = form.save(commit=False)
            updated_category.slug = slugify(updated_category.name)  # Generate new slug
            updated_category.save()

            # Redirect all related website URLs
            return redirect('view_category')

    else:
        form = CategoryForm(instance=category)

    return render(request, 'admin_pages/update_category.html', {'form': form, 'category': category})


@login_required(login_url='user_login')
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)  # ✅ Fetch category properly
    category.delete()
    return redirect("view_category")


# Websitee

@login_required(login_url='user_login')
def add_website(request):
    categories = Category.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        name = request.POST.get("name")
        slug = request.POST.get("slug") or slugify(name)  # Ensure slug is generated
        main_title = request.POST.get("main_title")
        meta_title = request.POST.get("meta_title")
        meta_description = request.POST.get("meta_description")
        description = request.POST.get("description")
        add_description = request.POST.get("add_description")
        add_title = request.POST.get("add_name")
        image = request.FILES.get("image")

        # Ensure unique slug per category
        base_slug = slug
        counter = 1
        while Website.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        website = Website.objects.create(
            category_id=category_id,
            name=name,
            slug=slug,
            main_title=main_title,
            meta_title=meta_title,
            meta_description=meta_description,
            description=description,
            add_description=add_description,
            image=image,
            add_title=add_title
            
        )

        # Handling multiple services
        service_headings = request.POST.getlist("service_heading[]")
        service_descriptions = request.POST.getlist("service_description[]")

        for heading, desc in zip(service_headings, service_descriptions):
            if heading.strip():
                Service.objects.create(website=website, heading=heading, description=desc)
                
        # Handle multiple FAQs
        faq_questions = request.POST.getlist("faq_question[]")
        faq_answers = request.POST.getlist("faq_answer[]")

        for question, answer in zip(faq_questions, faq_answers):
            if question.strip() and answer.strip():
                WebsiteFAQ.objects.create(website=website, question=question, answer=answer)

        # messages.success(request, "Website and services added successfully!")
        # return redirect(f"/{website.category.slug}/{website.slug}/")
        return redirect('view_websites')

    return render(request, "admin_home/add_website.html", {"categories": categories})


@login_required(login_url='user_login')
def view_websites(request):
    websites = Website.objects.prefetch_related('services').all().order_by('-id')
    return render(request, 'admin_home/view_website.html', {'websites': websites})

@login_required(login_url='user_login')
def update_website(request, website_id):
    website = get_object_or_404(Website, id=website_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        # Update website details
        website.category_id = request.POST.get('category')
        website.name = request.POST.get('name')
        website.slug = request.POST.get('slug')
        website.main_title = request.POST.get("main_title")
        website.meta_title = request.POST.get('meta_title')
        website.meta_description = request.POST.get('meta_description')
        website.description = request.POST.get('description')
        website.add_title = request.POST.get('add_name')
        website.add_description = request.POST.get('add_description')
      

        # Handle Image Upload
        if 'image' in request.FILES:
            website.image = request.FILES['image']

        website.save()

        # Clear existing services and add new ones
        website.services.all().delete()  # Delete old services
        service_headings = request.POST.getlist('service_heading[]')
        service_descriptions = request.POST.getlist('service_description[]')

        for heading, description in zip(service_headings, service_descriptions):
            if heading and description:  # Ensure fields are not empty
                Service.objects.create(website=website, heading=heading, description=description)
                
        # Update FAQs
        website.websitefaq_set.all().delete()
        faq_questions = request.POST.getlist('faq_question[]')
        faq_answers = request.POST.getlist('faq_answer[]')

        for question, answer in zip(faq_questions, faq_answers):
            if question.strip() and answer.strip():
                WebsiteFAQ.objects.create(website=website, question=question, answer=answer)


        # messages.success(request, "Website updated successfully!")
        return redirect('view_websites')  # Redirect to the view_websites page

    return render(request, 'admin_pages/update_website.html', {'website': website, 'categories': categories})

@login_required(login_url='user_login')
def delete_website(request, website_id):
    website = get_object_or_404(Website, id=website_id)
    website.delete()
    # messages.success(request, "Website deleted successfully!")
    return redirect('view_websites') 



@login_required(login_url='user_login')
def add_job_details(request):
    if request.method == 'POST':
        form = CareerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('view_job_details') 
    else:
        form = CareerForm()

    return render(request, 'admin_home/add_job_details.html', {'form': form})

@login_required(login_url='user_login')
def view_job_details(request):
    job_details = Career_Model.objects.all().order_by('-id')
    return render(request, 'admin_home/view_job_details.html', {'job_details': job_details})

@login_required(login_url='user_login')
def update_job_details(request, id):
    job_details = get_object_or_404(Career_Model, id=id)
    if request.method == 'POST':
        form = CareerForm(request.POST, request.FILES, instance=job_details)
        if form.is_valid():
            form.save()
            return redirect('view_job_details')
    else:
        form = CareerForm(instance=job_details)
    return render(request, 'admin_pages/update_job_details.html', {'form': form, 'job_details': job_details})


@login_required(login_url='user_login')
def delete_job_details(request,id):
    job_details = Career_Model.objects.get(id=id)
    job_details.delete()
    return redirect('view_job_details')

@login_required(login_url='user_login')
def view_candidate_details(request):
    certificates = Candidate.objects.all().order_by('-id')
    return render(request, 'admin_home/view_candidate_certificate.html', {'certificates': certificates})


@login_required(login_url='user_login')
def delete_candidate_certificates(request, id):
    candidate = get_object_or_404(Candidate, id=id)
    candidate.delete()
    return redirect('view_candidate_details')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import PromotionalBanner
from .forms import PromotionalBannerForm

# # Public view (for index page)
# def index(request):
#     # Get the highest priority active banner
#     active_banner = PromotionalBanner.objects.filter(
#         status='active',
#         end_date__gte=timezone.now()
#     ).first()
    
#     context = {
#         'active_banner': active_banner,
#         # ... your other context variables
#     }
#     return render(request, 'index.html', context)

# Admin views
@login_required
def banner_list(request):
    """List all promotional banners"""
    banners = PromotionalBanner.objects.all()
    
    # Add active status for each banner
    for banner in banners:
        banner.is_currently_active = banner.is_active()
    
    context = {
        'banners': banners
    }
    return render(request, 'admin_home/banner_list.html', context)

@login_required
def add_banner(request):
    """Add new promotional banner"""
    if request.method == 'POST':
        form = PromotionalBannerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Promotional banner added successfully!')
            return redirect('banner_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PromotionalBannerForm()
    
    context = {
        'form': form,
        'action': 'Add'
    }
    return render(request, 'admin_home/add_banner.html', context)

@login_required
def update_banner(request, pk):
    """Update existing promotional banner"""
    banner = get_object_or_404(PromotionalBanner, pk=pk)
    
    if request.method == 'POST':
        form = PromotionalBannerForm(request.POST, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Promotional banner updated successfully!')
            return redirect('banner_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PromotionalBannerForm(instance=banner)
    
    context = {
        'form': form,
        'banner': banner,
        'action': 'Update'
    }
    return render(request, 'admin_home/add_banner.html', context)

@login_required
def delete_banner(request, pk):
    """Delete promotional banner"""
    banner = get_object_or_404(PromotionalBanner, pk=pk)
    
    if request.method == 'POST':
        banner.delete()
        messages.success(request, 'Promotional banner deleted successfully!')
        return redirect('banner_list')
    
    return redirect('banner_list')