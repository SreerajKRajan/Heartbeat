from django.shortcuts import render,redirect
from django.contrib import messages
from . models import *
from django.http import JsonResponse



# Create your views here.

def products_list(request):
    products = Product.objects.all().order_by('-id')
    product_count = products.count()
    context = {
        'products': products,
        'products_count': product_count
    }
    return render(request,'admin_side/products_list.html', context)


def add_product(request):
    category = Category.objects.all()
    brand = Brand.objects.all()
    products = Product.objects.all()

    context = {
        'category': category,
        'brand': brand,
        'products': products
    }

    if request.method == "POST":
        product_title = request.POST.get('product_title')
        category_id = request.POST.get('category_id')
        brand_id = request.POST.get('Brand')
        description = request.POST.get('description')
        base_price = request.POST.get('price')
        # brand = Brand.objects.filter(brand_name=brand_id)
        # brand = brand.id
        category = Category.objects.get(id = category_id)
        brand = Brand.objects.get(id = brand_id)

        product = Product(
            product_name = product_title,
            category = category,
            brand = brand,
            description = description,
            base_price = base_price
        )

        product.save()
        messages.success(request, 'Product Added.')
        return redirect('products_list')
    return render(request, 'admin_side/add_product.html', context)


def edit_product(request,product_id):
   
    print(product_id)
    category = Category.objects.all()
    brand = Brand.objects.all()
    products = Product.objects.filter(id = product_id)
    product_instance = products.first()

    context = {
        'category': category,
        'brand'   : brand,
        'products': product_instance,
    }

    if request.method == "POST":
        product_title = request.POST.get('product_title')
        category_id   = request.POST.get('category_id')
        brand_id      = request.POST.get('brand')
        description   = request.POST.get('description')
        base_price    = request.POST.get('price')
        category      = Category.objects.get(id = category_id)
        brand         = Brand.objects.get(id = brand_id)

        product = Product.objects.filter(id = product_instance.id)
        product.product_name = product_title
        product.category     = category_id
        product.brand        = brand_id
        product.description  = description
        product.base_price   = base_price
        product.save()

        messages.success(request, 'Product Edited.')
        return redirect('products_list', product_id.id)
    
    return render(request, "admin_side/edit_product.html", context)
################### Product Available ###############################

def list_product(request, product_id):
    product = Product.objects.get(id = product_id)
    product.is_available = True
    product.save()
    return redirect('products_list')

################### Product Unavaliable ###############################

def unlist_product(request, product_id):
    product = Product.objects.get(id = product_id)
    product.is_available = False
    product.save()
    return redirect('products_list')



def product_variant_list(request, product_id):
    product = Product.objects.get(id = product_id)
    product_variant = Product_Variant.objects.filter(product = product)

    context = {'product_variant': product_variant}

    return render(request, 'admin_side/product_variant.html', context)


def add_product_variant(request):
   
    category = Category.objects.all()
    brand    = Brand.objects.all()
    products = Product.objects.all()
    colour= Colour.objects.all()

    if request.method == "POST":
        product         = request.POST.get('product')
        sku_id          = request.POST.get('sku_id')
        max_price       = request.POST.get('max_price')
        product_image   = request.FILES.getlist('product_image')
        sale_price      = request.POST.get('sale_price')
        stock           = request.POST.get('stock')      
        thumbnail_image = request.FILES.get('thumbnail_image')
        req_atri = request.POST.getlist('colour_value')


        # attribute_ids = []
        # for x in range(1, Colour_count+1):
        #     if req_atri != 'None':
        #         attribute_ids.append(req_atri)

        product_id = Product.objects.get(id = product)

        product_variant = Product_Variant(
            product         = product_id, 
            sku_id          = sku_id,
            max_price       = max_price, 
            sale_price      = sale_price, 
            stock           = stock, 
            thumbnail_image = thumbnail_image
        )

        product_variant.save()
        product_variant.colour.set(req_atri)
        for image in product_image:
            Additional_Product_Image.objects.create(product_varient=product_variant, image=image)

        messages.success(request, 'Product Variation Added')
        return redirect('add_product')
    
    context = {
        'category': category,
        'brand':brand,
        'products':products,
        'colour': colour,
    }

    return render(request, 'admin_side/add_product_variant.html', context)

##############   Unlist / List Product Variants   #############

def toggle_product_variant(request,id):
    product_variant = Product_Variant.objects.get(id=id)
    product_variant.is_active = not product_variant.is_active
    product_variant.save()
    response_data = {
        'status': 'success',
        'message': 'Product variant toggled successfully.',
        'product_id': product_variant.product.id,  
    }
    return JsonResponse(response_data)

def edit_product_variant(request,product_id):
    old_product = Product_Variant.objects.get(id=product_id)
    products =Product.objects.all()

   
    # attributes = Attribute.objects.prefetch_related('attribute_value_set').filter(is_active=True)
#    to get the old varient
    # attr_values_list = [item['attribute_value'] for item in old_product.attributes.all().values('attribute_value')]
  

    # attribute_dict = {}
    # for attribute in attributes:
    #     attribute_values = attribute.attribute_value_set.filter(is_active=True)
    #     attribute_dict[attribute.attribute_name] = attribute_values  
    #      #to show how many atribute in fronend
    #     attribute_values_count = attributes.count()  

        
    if request.method == "POST":
        
        product         = request.POST['product']
        sku_id          = request.POST['sku_id']
        max_price       = request.POST['max_price']
        product_image   = request.FILES.getlist('product_image')
        sale_price      = request.POST['sale_price']
        stock           = request.POST['stock']      
        thumbnail_image = request.FILES.get('existing_product_images')     
       
        #getting all atributes  
        attribute_values = request.POST.getlist('attributes')
       
        attribute_ids = []
        for req_atri in attribute_values:
         if req_atri != 'None':
           attribute_ids.append(req_atri)   

        product_id =Product.objects.get(id=product)
      
        old_product.sku_id          = sku_id
        old_product.max_price       = max_price 
        old_product.sale_price      = sale_price 
        old_product.stock           = stock 

        if thumbnail_image != None:
           old_product.thumbnail_image = thumbnail_image
        else:
           pass   
        
        
        old_product.save()
        old_product.attributes.set(attribute_ids)
        if not product_image  :
            for image in product_image:
                Additional_Product_Image.objects.create(product_variant=old_product,image=image)
        else:
            old_product.additional_product_images.all().delete()
            for image in product_image:
                Additional_Product_Image.objects.create(product_variant=old_product,image=image)
        messages.success(request, 'Product variation Added.')
        return redirect('all-variant-product',product_id=product_id.id)
        # return redirect(request.META.get('HTTP_REFERER', 'all-variant-product'))
     
    
    
    context={
        "old_product":old_product,
        "products": products, 
        # 'attribute_dict': attribute_dict,
        # 'attr':attr_values_list,
    }

    return render(request,"admin_templates/edit_product_variant.html",context)
