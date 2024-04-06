from django.urls import path
from . import views
from product_management import views as productView

urlpatterns = [
    path('admin-login/',views.admin_login,name='admin_login'),
    path('admin-dashboard/',views.admin_dashboard,name='admin_dashboard'),  
    path('admin-logout',views.admin_logout,name='admin_logout'),

    ################## User management ####################################

    path('all-users/',views.all_users,name='all_users'),
    path('user-details/', views.user_details, name='user_details'),
    path('all-users/blockuser/', views.blockuser, name='blockuser'),

    ################# Product management ##################################

    path('products-list/',productView.products_list,name='products_list'), 
    path('add-product/',productView.add_product,name='add_product'),
    path('edit-product/<int:product_id>/',productView.edit_product,name='edit_product'),
    path('product-variant-list/<int:product_id>/',productView.product_variant_list,name='product_variant_list'), 
    path('add-productvariant/',productView.add_product_variant,name='add_product_variant'),
    path('edit-product-variant/<int:product_id>/',productView.edit_product_variant,name='edit_product_variant'),
    path('unlist-product/<int:product_id>/',productView.unlist_product,name='unlist-product'), # Making it unavailable
    path('list-product/<int:product_id>/',productView.list_product,name='list-product'),       # Making it available
    path("list-product-variant/<int:product_id>/",productView.list_product_variant, name="list_product_variant"),
    path('unlist-product-variant/<int:product_id>/', productView.unlist_product_variant, name='unlist_product_variant'),

    ################# Category management ##################################
    
    path('manage-category/',views.manage_category,name='manage_category'),
    path('add-category/',views.add_category,name='add_category'),
    path('edit-category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('unlist-category/<int:category_id>/',views.unlist_category,name='unlist_category'), # Making it unavailable
    path('list-category/<int:category_id>/',views.list_category,name='list_category'),       # Making it available




    # path('admin-',views.admin_,name='admin_')
    # path('',views.adminhome,name='adminhome'),
    # path('login/',views.admin_login,name='admin_login'),
    # path('logout/',views.adminlogout,name='adminlogout'),
    # path('product/',views.productdetail,name='productdetail'),
    # path('add-product/',views.addproduct,name='addproduct'),
    # path('edit-product/<int:product_id>',views.editproduct,name='editproduct'),
    # path('add-category/',views.addcategory,name='addcategory'),
    
    # path('user-management/', views.user_management, name='user_management'),
    # path('category-management/',views.categorymanagement,name='categorymanagement'),

    # path('blockuser/<int:user_id>/', views.blockuser, name='blockuser'),
    # path('unblockuser/<int:user_id>/', views.unblockuser, name='unblockuser'),

    # path('deactivate-product/<int:product_id>/',views.deactivateproduct,name='deactivateproduct'),
    # path('activate-product/<int:product_id>/',views.activateproduct,name='activateproduct'),
]