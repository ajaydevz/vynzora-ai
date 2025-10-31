from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Blog, Website, Category

# Define the site domain correctly
SITE_DOMAIN = "https://vynzora.com"

class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return [
            "index", "about", "portfolio", "contact", "advertising",
            "web_development", "digital_marketing", "trademark", "branding",
            "it_solutions", "privacy_and_policy", "terms_and_conditions",
            "careers", "blog"
        ]
    def location(self, item):
        return reverse(item)

SITE_DOMAIN = "https://vynzora.com"

class BlogSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Blog.objects.all()

    def location(self, obj):
        return f"{SITE_DOMAIN}{reverse('blog_details', kwargs={'slug': obj.slug})}"

class WebsiteSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Website.objects.all()

    def location(self, obj):
        return f"{SITE_DOMAIN}{reverse('website_detail', kwargs={'category_slug': obj.category.slug, 'website_slug': obj.slug})}"

class CategorySitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return f"{SITE_DOMAIN}{reverse('view_category')}"
