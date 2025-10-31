from django.db import models
from django.utils.timezone import now
from ckeditor.fields import RichTextField
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, max_length=255, help_text="Unique URL identifier for the category")
    created_date = models.DateTimeField(default=now, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk:  # If updating an existing category
            old_category = Category.objects.get(pk=self.pk)
            if old_category.name != self.name:  # Check if name is changed
                self.slug = slugify(self.name)  # Generate new slug

                # Update related Website URLs
                from vynzora_app.models import Website  # Import inside to avoid circular import
                Website.objects.filter(category=self).update(category=self)  # Update category reference

        else:
            self.slug = slugify(self.name)  # Generate slug for new category

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Website(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="websites"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    meta_title = models.CharField(max_length=200)
    main_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField()
    image = models.ImageField(upload_to="website_images/", blank=True, null=True)
    created_date = models.DateTimeField(default=now, blank=True, null=True)
    add_description = models.TextField()
    add_title = models.CharField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it's empty
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Website.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug  # Assign the unique slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    
    
class Services(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="services/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ServiceOffer(models.Model):
    service = models.ForeignKey(Services, related_name="offers", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return f"{self.service.name} - {self.title}"


class ServiceProcessStep(models.Model):
    service = models.ForeignKey(Services, related_name="process_steps", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=250)  # short single-line description

    def clean(self):
        if ServiceProcessStep.objects.filter(service=self.service).count() >= 4:
            raise ValidationError("Each Service can have a maximum of 4 process steps.")

    def __str__(self):
        return f"{self.service.name} - Step: {self.title}"


class ServiceFAQ(models.Model):
    service = models.ForeignKey(Services, related_name="faqs", on_delete=models.CASCADE)
    question = models.CharField(max_length=300)
    answer = models.TextField()

    def clean(self):
        if ServiceFAQ.objects.filter(service=self.service).count() >= 6:
            raise ValidationError("Each Service can have a maximum of 6 FAQs.")

    def __str__(self):
        return f"FAQ: {self.question}"


class ContactModel(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Contact"


# Client Reviews
class ClientReview(models.Model):
    client_name = models.CharField(max_length=100, null=True, blank=True)
    client_image = models.ImageField(upload_to='client_images/', null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    # rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], default=5)
    
    def __str__(self):
        return f"{self.client_name} - {self.designation}"

# Clients Logo

class Client_Logo(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    logo = models.ImageField(upload_to='team_images/')

    def __str__(self):
        return self.name


# Technologies
class Technologies(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    logo = models.ImageField(upload_to='team_images/')

    def __str__(self):
        return self.name

# Blog


#  Team
class Team(models.Model):
    client_name = models.CharField(max_length=100, null=True, blank=True)
    client_image = models.ImageField(upload_to='client_images/', null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
   
    def __str__(self):
        return f"{self.client_name} - {self.designation}"


    # Portfolio 
class ProjectModel(models.Model):
    project_name = models.CharField(max_length=100, null=True, blank=True)
    website_link = models.CharField(max_length=200, null=True, blank=True)
    project_image = models.ImageField(upload_to='project_images/', null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    
    
    def __str__(self):
        return self.project_name


# Certificate
class Certificates(models.Model):
    id1 = models.CharField(max_length=100)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    join_date = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    pdf_file = models.FileField(upload_to='pdfs/')  
    def __str__(self):
        return f"{self.id1}"


# Websss
from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now



    
class Blog(models.Model):
    slug = models.SlugField(unique=True, max_length=255, help_text="Unique URL-friendly identifier for the blog")
    meta_title = models.CharField(max_length=200, help_text="SEO-friendly title for the blog")
    meta_description = models.TextField(help_text="SEO-friendly description for the blog")
    name = models.CharField(max_length=200,blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to='blog_images/',blank=True, null=True)
    created_date = models.DateTimeField(default=now,blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Auto-generate slug from title
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Service(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="services")
    heading = models.CharField(max_length=200, verbose_name="Service Heading")
    description = models.TextField(verbose_name="Service Description")

    class Meta:
        constraints = []  # ❌ Removed uniqueness constraint on (website, heading)

    def __str__(self):
        return f"{self.heading} - {self.website.name}"
    
    
    



# Careeers
class Career_Model(models.Model): 
    
    JOB_TYPES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
        ('remote', 'Remote'),
    )   
    job_position = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50, choices=JOB_TYPES)
    company_name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    salary = models.IntegerField()
    job_details = RichTextField(max_length=20000)
    
    posted_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    post_end_date = models.DateTimeField(null=True, blank=True)


    
    def is_active(self):
        return self.post_end_date >= timezone.now()



# Candidate
class Candidate(models.Model):
    EXPERIENCE_CHOICES = [
        ('0-1 years', '0 to 1 Year'),
        ('1-3 years', '1 to 3 Years'),
        ('3-5 years', '3 to 5 Years'),
        ('5+ years', '5+ Years'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    phone = models.CharField(max_length=20)
    job_position = models.ForeignKey(
        Career_Model,
        on_delete=models.SET_NULL,
        null=True,
        related_name='candidates'
    )
    experience = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES)
    linkedin_profile = models.URLField(max_length=255, blank=True, null=True)
    portfolio_url = models.URLField(max_length=255, blank=True, null=True)
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    

    def __str__(self):
        return self.name



from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class PromotionalBanner(models.Model):
    OCCASION_CHOICES = [
        ('black_friday', 'Black Friday'),
        ('christmas', 'Christmas'),
        ('new_year', 'New Year'),
        ('onam', 'Onam'),
        ('eid', 'Eid'),
        ('diwali', 'Diwali'),
        ('easter', 'Easter'),
        ('valentine', 'Valentine\'s Day'),
        ('independence', 'Independence Day'),
        ('custom', 'Custom Occasion'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    # Basic Info
    title = models.CharField(max_length=200, help_text="Main banner title")
    subtitle = models.CharField(max_length=300, blank=True, help_text="Optional subtitle")
    occasion = models.CharField(max_length=50, choices=OCCASION_CHOICES, default='custom')
    custom_occasion = models.CharField(max_length=100, blank=True, help_text="If 'Custom Occasion' selected")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Offer Details
    discount_text = models.CharField(max_length=100, help_text="e.g., '80% OFF'")
    offer_description = models.CharField(max_length=300, help_text="Brief offer description")
    
    # Timer Settings
    show_timer = models.BooleanField(default=True, help_text="Show countdown timer")
    end_date = models.DateTimeField(help_text="Offer expiration date & time")
    
    # Visual Customization
    hex_validator = RegexValidator(regex='^#([A-Fa-f0-9]{6})$', message='Enter a valid hex color (e.g., #FF5733)')
    background_color = models.CharField(max_length=7, default='#000000', validators=[hex_validator])
    text_color = models.CharField(max_length=7, default='#FFFFFF', validators=[hex_validator])
    accent_color = models.CharField(max_length=7, default='#9b59b6', validators=[hex_validator])
    
    # Call to Action
    cta_text = models.CharField(max_length=100, default='Claim deal')
    cta_link = models.URLField(help_text="Button destination URL")
    
    # Additional Info
    additional_info = models.CharField(max_length=200, blank=True, help_text="Extra info (e.g., '30-day money-back guarantee')")
    
    # Priority
    priority = models.IntegerField(default=0, help_text="Higher number = higher priority")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = 'Promotional Banner'
        verbose_name_plural = 'Promotional Banners'
    
    def __str__(self):
        occasion_display = self.custom_occasion if self.occasion == 'custom' else self.get_occasion_display()
        return f"{self.title} - {occasion_display}"
    
    def is_active(self):
        """Check if banner should be displayed"""
        if self.status != 'active':
            return False
        if self.end_date < timezone.now():
            return False
        return True
    
    def get_occasion_name(self):
        """Get the display name for occasion"""
        if self.occasion == 'custom':
            return self.custom_occasion
        return self.get_occasion_display()
    
    
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_date = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.category.title()} FAQ: {self.question}"
    

class WebsiteFAQ(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=200)
    answer = models.TextField()

    def __str__(self):
        return f"FAQ for {self.website.website_name}: {self.question[:50]}"