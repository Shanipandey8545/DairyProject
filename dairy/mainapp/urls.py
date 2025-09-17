from django.urls import path
from . import views,super_admin


urlpatterns = [

    path('plans/', super_admin.subscription_plan_list, name='subscription_plan_list'),
    path('plans/add/', super_admin.add_subscription_plan, name='add_subscription_plan'),
    path('plans/edit/<int:plan_id>/', super_admin.edit_subscription_plan, name='edit_subscription_plan'),
    path('plans/edit/<int:plan_id>/', super_admin.delete_subscription_plan, name='delete_subscription_plan'),
    

    path('', views.home_view, name='home'),
    path('signup/', views.signup_dairy_view, name='signup'),
    # path('choose-plan/<int:main_dairy_id>/', views.choose_plan_view, name='choose_plan'),
    # path('activate-free/<int:main_dairy_id>/<int:plan_id>/', views.activate_free_plan_view, name='activate_free_plan'),
    # path('create-order/', views.create_razorpay_order, name='create_order'),
    # path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    
    ## branch 
    path('branch_dairy_list/', views.branch_dairy_list, name='branch_dairy_list'),
    path('add_branch_dairy', views.add_branch_dairy, name='add_branch_dairy'),
    path('edit_branch_dairy/<int:dairy_id>/', views.edit_branch_dairy, name='edit_branch_dairy'),
    path('delete_branch_dairy/<int:dairy_id>/', views.delete_branch_dairy, name='delete_branch_dairy'),
    
    
    path('user-list/', views.user_list_view, name='user_list'),
    path('user/add/', views.add_user_view, name='add_user'),
    path('edit-user/<int:pk>/', views.edit_user_view, name='edit_user'),
    path('delete-user/<int:pk>/', views.delete_user_view, name='delete_user'),
    
    path('milk-type/', views.milk_type_list, name='milk_type_list'),
    path('milk-type/add/', views.add_milk_type, name='add_milk_type'),
    path('milk-type/edit/<int:pk>/', views.edit_milk_type, name='edit_milk_type'),
    path('milk-type/delete/<int:pk>/', views.delete_milk_type, name='delete_milk_type'),


    path('milk-collections/', views.milk_collection_list, name='milk_collection_list'),
    path('collections/update-payment-status/', views.update_payment_status, name='update_payment_status'),
    
    path('milk-collection/', views.milk_collection_add, name='milk_collection'),
    path('milk-collection/edit/<int:pk>/', views.edit_milk_collection, name='edit_milk_collection'),
    path('milk-collection/delete/<int:pk>/', views.delete_milk_collection, name='delete_milk_collection'),
    path('milk-sale/', views.milk_sale_add, name='milk_sale'),
    path('payment-history/', views.payment_history, name='payment_history'),

    path('milk-stock/', views.milk_stock_view, name='milk_stock'),


]
