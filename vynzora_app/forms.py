from django import forms
from .models import ContactModel, ClientReview, Client_Logo, Technologies, Blog, Team, ProjectModel, Certificates, Category, Website, Career_Model, Candidate
from .models import Services, ServiceOffer, ServiceProcessStep, ServiceFAQ
from django.forms import inlineformset_factory

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = ["name", "description", "image"]


OfferFormSet = inlineformset_factory(
    Services, ServiceOffer,
    fields=["title", "description"],
    extra=3,  # You can change count shown initially
    can_delete=True
)

StepFormSet = inlineformset_factory(
    Services, ServiceProcessStep,
    fields=["title", "tagline"],
    extra=4,  # exactly 4 steps input allowed
    max_num=4,
    can_delete=True
)

FAQFormSet = inlineformset_factory(
    Services, ServiceFAQ,
    fields=["question", "answer"],
    extra=6,  # max 6 FAQ inputs
    max_num=6,
    can_delete=True
)

# Contact us
class ContactModelForm(forms.ModelForm):
    class Meta:
        model = ContactModel
        fields = '__all__'

# Clien Review
class ClientReviewForm(forms.ModelForm):
    class Meta:
        model = ClientReview
        fields = '__all__'

# Clients Logo
class Client_Logo_Form(forms.ModelForm):
    class Meta:
        model = Client_Logo
        fields = '__all__'

# Technologies
class TechnologiesForm(forms.ModelForm):
    class Meta:
        model = Technologies
        fields = '__all__'


# Blog
class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = '__all__'

# Team
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'


# Portfolio 

# class ProjectModelForm(forms.ModelForm):
#     class Meta:
#         model = ProjectModel
#         fields = '__all__'

class ProjectModelForm(forms.ModelForm):
    class Meta:
        model = ProjectModel
        fields = ['project_name','website_link','project_image']
       

# Certificate

class CertificatesForm(forms.ModelForm):
    class Meta:
        model = Certificates
        fields = '__all__'


# Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

# Website
class WebsiteForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = '__all__'


# careeers

class CareerForm(forms.ModelForm):
    class Meta:
        model = Career_Model
        fields = '__all__'

# Candidate

# forms.py
from django import forms
from .models import Candidate, Career_Model

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'email', 'phone', 'job_position', 'experience', 
                 'linkedin_profile', 'portfolio_url', 'cover_letter', 'resume']
        
    


from django import forms
from .models import PromotionalBanner
from django.utils import timezone

class PromotionalBannerForm(forms.ModelForm):
    class Meta:
        model = PromotionalBanner
        fields = [
            'title', 'subtitle', 'occasion', 'custom_occasion', 'status',
            'discount_text', 'offer_description', 'show_timer', 'end_date',
            'background_color', 'text_color', 'accent_color',
            'cta_text', 'cta_link', 'additional_info', 'priority'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter banner title (e.g., Black Friday sale)'
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional subtitle'
            }),
            'occasion': forms.Select(attrs={'class': 'form-control'}),
            'custom_occasion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter custom occasion name'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'discount_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 80% OFF'
            }),
            'offer_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the offer'
            }),
            'show_timer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'background_color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'text_color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'accent_color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'cta_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Button text'
            }),
            'cta_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/offer'
            }),
            'additional_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional additional information'
            }),
            'priority': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        occasion = cleaned_data.get('occasion')
        custom_occasion = cleaned_data.get('custom_occasion')
        end_date = cleaned_data.get('end_date')
        
        # Validate custom occasion
        if occasion == 'custom' and not custom_occasion:
            raise forms.ValidationError('Please provide a custom occasion name.')
        
        # Validate end date
        if end_date and end_date < timezone.now():
            raise forms.ValidationError('End date must be in the future.')
        
        return cleaned_data
        
