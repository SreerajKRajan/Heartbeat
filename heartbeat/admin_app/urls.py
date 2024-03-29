from django.urls import path
from . import views
from product_management import views as productView

urlpatterns = [
    path('admin-login/',views.admin_login,name='admin_login'),
    path('admin-dashboard',views.admin_dashboard,name='admin_dashboard'),  
    # path('admin-products_list',views.admin_products_list,name='admin_products_list'),
    path('admin-orders',views.admin_orders,name='admin_orders'),
    path('admin-catagories',views.admin_catagories,name='admin_catagories'),
    # path('admin-add-products',views.admin_add_products,name='admin_add_products'),
    # path('admin-users-list',views.admin_users_list,name='admin_users_list'),
    path('admin-logout',views.admin_logout,name='admin_logout'),

    ################## User management ####################################

    path('all-users',views.all_users,name='all_users'),
    # path('activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    # path('deactivate-user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('user-details/', views.user_details, name='user_details'),
    path('blockuser/', views.blockuser, name='blockuser'),

    ################# Product management ##################################

    path('products-list/',productView.products_list,name='products_list'), 
    path('add-product/',productView.add_product,name='add_product'),
    path('edit-product/<int:product_id>/',productView.edit_product,name='edit_product'),
    path('product-variant-list/<int:product_id>/',productView.product_variant_list,name='product_variant_list'), 
    path('add-productvariant-/',productView.add_product_variant,name='add_product_variant'),
    path('edit-product-variant/<int:product_id>/',productView.edit_product_variant,name='edit_product_variant'),
    path('unlist-product/<int:product_id>/',productView.unlist_product,name='unlist-product'), # Making it unavailable
    path('list-product/<int:product_id>/',productView.list_product,name='list-product'),       # Making it available
    path('toggle-product/<int:id>/',productView.toggle_product_variant,name='toggle-product-variant'),     


    
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