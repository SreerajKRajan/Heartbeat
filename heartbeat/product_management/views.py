from django.shortcuts import render,redirect
from django.contrib import messages
from . models import *
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


# Create your views here.

def products_list(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        category = Category.objects.all()
        products = Product.objects.all().order_by('-id')
        product_count = products.count()
        context = {
            'category': category,
            'products': products,
            'products_count': product_count
        }
        return render(request,'admin_side/products_list.html', context)
    return redirect('admin_login')



def add_product(request):
    if request.user.is_authenticated and request.user.is_superadmin:
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

            # if Product.objects.filter(product_title = product_title).exists():
            #     messages.warning(request, 'Product already exists')
            #     return redirect('add_product')
            if not product_title:
                messages.warning(request, 'Product title field cannot be empty')
                return redirect('add_product')
            if not description:
                messages.warning(request, 'Description field cannot be empty')
                return redirect('add_product')
            if not base_price:
                messages.warning(request, 'Price field cannot be empty')
                return redirect('add_product')
            if ' ' in base_price:
                messages.warning(request, 'Price field cannot be empty')
                return redirect('add_product')
            
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
    return redirect('admin_login')



def edit_product(request, product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        category = Category.objects.all()
        brand = Brand.objects.all()
        product_instance = Product.objects.get(id=product_id)
        print("Product Brand\ ID:", product_instance.description)  # Debugging statement


        context = {
            'category': category,
            'brand': brand,
            'product': product_instance,
        }

        if request.method == "POST":
            product_title = request.POST.get('product_title')
            category_id = request.POST.get('category_id')
            brand_id = request.POST.get('brand_id')
            description = request.POST.get('description')
            base_price = request.POST.get('price')
            category = Category.objects.get(id=category_id)
            brand = Brand.objects.get(id=brand_id)

            # Update the product instance directly
            product_instance.product_name = product_title
            product_instance.category = category
            product_instance.brand = brand
            product_instance.description = description
            product_instance.base_price = base_price
            product_instance.save()

            messages.success(request, 'Product Edited.')
            return redirect('products_list')

        return render(request, "admin_side/edit_product.html", context)
    return redirect('admin_login')

################### Product Available ###############################

def list_product(request, product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        product = Product.objects.get(id = product_id)
        product.is_available = True
        product.save()
        return redirect('products_list')
    return redirect('admin_login')


################### Product Unavaliable ###############################

def unlist_product(request, product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        product = Product.objects.get(id = product_id)
        product.is_available = False
        product.save()
        return redirect('products_list')
    return redirect('admin_login')



def product_variant_list(request, product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        product = Product.objects.get(id = product_id)
        product_variant = Product_Variant.objects.filter(product = product)
    
        context = {'product_variant': product_variant}
    
        return render(request, 'admin_side/product_variant.html', context)
    return redirect('admin_login')



def add_product_variant(request):
    if request.user.is_authenticated and request.user.is_superadmin:
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
    return redirect('admin_login')


##############   List / Unist Product Variants   #############

def list_product_variant(request, product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        product_variant = Product_Variant.objects.get(id = product_id)
        product_variant.is_active = True
        product_variant.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('admin_login')


def unlist_product_variant(request, product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        product_variant = Product_Variant.objects.get(id = product_id)
        product_variant.is_active = False
        product_variant.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('admin_login')


def edit_product_variant(request,product_id):
    if request.user.is_authenticated and request.user.is_superadmin:
        old_product = Product_Variant.objects.get(id=product_id)
        product11 = Product.objects.get(id = old_product.product.id)
        print("vvvvvvvvvvvvvvvvv",product11)
        products = Product.objects.all()

        if request.method == "POST":
            product         = request.POST['product']
            sku_id          = request.POST['sku_id']
            colour          = request.POST['colour_value']
            max_price       = request.POST['max_price']
            product_image   = request.FILES.getlist('product_image')
            sale_price      = request.POST['sale_price']
            stock           = request.POST['stock']      
            thumbnail_image = request.FILES.get('existing_product_images')     
 

            product_instance = Product.objects.get(id=product)

            old_product.product         = product_instance
            old_product.sku_id          = sku_id
            old_product.colour.set(colour)
            old_product.max_price       = max_price 
            old_product.sale_price      = sale_price 
            old_product.stock           = stock 

            if thumbnail_image != None:
               old_product.thumbnail_image = thumbnail_image
            else:
               pass   
           
           
            old_product.save()
            if not product_image:
                for image in product_image:
                    Additional_Product_Image.objects.create(product_variant=old_product, image=image)
            else:
                old_product.additional_product_images.all().delete()
                for image in product_image:
                    Additional_Product_Image.objects.create(product_variant=old_product, image=image)
            messages.success(request, 'Product variation Edited.')
            return redirect('product_variant_list',product11.id)
            # return redirect(request.META.get('HTTP_REFERER', 'all-variant-product'))

        colour = Colour.objects.filter(is_active = True)


        context={
            "old_product":old_product,
            "products": products,
            "colour":colour,
            "product_id":product_id
        }

        return render(request,"admin_side/edit_product_variant.html",context)
    return redirect('admin_login')

