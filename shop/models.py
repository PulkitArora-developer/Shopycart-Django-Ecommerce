from django.db import models
from django.urls import reverse
from django.db.models import Avg,Count
from category.models import Category
from accounts.models import Account

class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    description = models.TextField(max_length=1000,blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])

    def avgRating(self):
        review = ReviewRating.objects.filter(product=self,status_flag=True).aggregate(average=Avg('rating'))
        avg = 0
        if review['average'] is not None:
            avg = float(review['average'])
        return avg

    def countRating(self):
        review = ReviewRating.objects.filter(product=self,status_flag=True).aggregate(count=Count('id'))
        count = 0
        if review['count'] is not None:
            count = int(review['count'])
        return count

    def __str__(self):
        return self.product_name


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)

    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active=True)


variation_choice = (
    ('color','color'),
    ('size','size')
)

class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=150,blank=True)
    review = models.TextField(max_length=500,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20,blank=True)
    status_flag = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class ProductGallery(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,default=None)
    image = models.ImageField(upload_to='store/products/')

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'product_gallery'
        verbose_name_plural = 'product gallery'