from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.db.models import UniqueConstraint, Q, F, Avg, Count

# Create your models here.

class Brand(models.Model):
    brand_name = models.CharField(max_length = 50, unique = True)
    is_active  = models.BooleanField(default = True)

    def __str__(self):
        return self.brand_name
    

class Category(models.Model):
    category_name = models.CharField(max_length = 100, unique = True)
    slug          = models.SlugField(max_length = 100, unique = True, blank = True)
    is_active     = models.BooleanField(default = True)

    class Meta:
        verbose_name        = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category',args=[self.slug])

    
    def save(self, *args, **kwargs):
        # Automatically generate the slug from the product name
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def __str__(self) :
        return self.category_name

    
class Product(models.Model):
    product_name   = models.CharField(max_length = 250, unique = True)
    slug           = models.SlugField(max_length = 250, unique = True)
    description    = models.TextField(max_length = 500, blank = True)
    is_available   = models.BooleanField(default = True)
    base_price     = models.DecimalField(max_digits = 8, decimal_places = 2)
    brand          = models.ForeignKey(Brand, on_delete = models.CASCADE)
    category       = models.ForeignKey(Category, on_delete = models.CASCADE)
    created_date   = models.DateTimeField(auto_now_add = True)
    modified_date  = models.DateTimeField(auto_now = True)

    def save(self, *args, **kwargs):
        product_slug_name = f'{self.brand.brand_name}-{self.product_name}-{self.category.category_name}'
        base_slug = slugify(product_slug_name)
        counter = Product.objects.filter(slug__startswith=base_slug).count()
        if counter > 0:
            self.product_slug = f'{base_slug}-{counter}'
        else:
            self.slug = base_slug
        super(Product, self).save(*args, **kwargs)
        
    def __str__(self) -> str:
        return self.brand.brand_name+"-"+self.product_name
    

    
class Colour (models.Model):
    colour_value = models.CharField(max_length = 100, unique = True)
    is_active       = models.BooleanField(default = True)

    def str(self):
        return self.colour_value
    

class Product_VariantManager(models.Manager):
    """
    Custom manager
    """
    def get_all_variant(self,product):
        # variant = super(Product_VariantManager, self).get_queryset().filter(product=product).values('sku_id','atributes__atribute_value','atributes__atribute__atribute_name')
        variant = (
                    super(Product_VariantManager, self)
                    .get_queryset()
                    .filter(product=product)
                    .values('sku_id')
                    # .annotate(
                    #     atribute_value=F('atributes__atribute_value'),
                    #     atribute_name=F('atributes__atribute__atribute_name')
                    # )
                )
        return  variant
    

class Product_Variant(models.Model):
    product              = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='products')
    sku_id               = models.CharField(max_length=30)
    colour               = models.ManyToManyField(Colour,related_name='colour')
    max_price            = models.DecimalField(max_digits=8, decimal_places=2)
    sale_price           = models.DecimalField(max_digits=8, decimal_places=2)
    stock                = models.IntegerField()
    product_variant_slug = models.SlugField( blank=True,max_length=200)
    thumbnail_image      = models.ImageField(upload_to='media/phtots/product_variant/')
    is_active            = models.BooleanField(default=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)



class Additional_Product_Image(models.Model):
    product_variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE, related_name='additional_product_images')
    image = models.ImageField(upload_to='media/photos/additional_photos')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.image.url    
