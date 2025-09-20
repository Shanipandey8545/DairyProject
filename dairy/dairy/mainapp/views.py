from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import json
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
import razorpay
from .utils import compute_expiry
# Home View
def home_view(request):
    return render(request, 'mainapp/home.html')





######################################################################################### start with plan +++++++++++++

# # ---- signup view (modified) ----
# def signup_dairy_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password1 = request.POST.get('password1')
#         password2 = request.POST.get('password2')
#         mobile = request.POST.get('mobile')
#         address = request.POST.get('address')
#         dairy_name = request.POST.get('dairy_name')
#         profile_image = request.FILES.get('profile_image')

#         # validations (same as your code)
#         if password1 != password2:
#             messages.error(request, "Passwords do not match.")
#             return redirect('signup')

#         if User.objects.filter(username=username).exists():
#             messages.error(request, "Username already exists.")
#             return redirect('signup')

#         if User.objects.filter(email=email).exists():
#             messages.error(request, "Email already in use.")
#             return redirect('signup')

#         if User.objects.filter(mobile=mobile).exists():
#             messages.error(request, "Mobile number already in use.")
#             return redirect('signup')

#         user = User.objects.create_user(
#             username=username,
#             first_name=username,
#             email=email,
#             password=password1,
#             mobile=mobile,
#             address=address,
#             role='Admin',
#             profile_image=profile_image
#         )

#         main_dairy = MainDairy.objects.create(name=dairy_name)
#         dairy = Dairy.objects.create(main_dairy=main_dairy, user=user, name=dairy_name, role='Main', is_main=True)
#         DairyUserProfile.objects.create(user=user, dairy=dairy)

#         login(request, user)
#         # Redirect to choose plan page after signup
#         return redirect('choose_plan', main_dairy.id)

#     return render(request, 'mainapp/signupmain_dairy.html')


# # ---- choose plan page ----
# def choose_plan_view(request, main_dairy_id):
#     main_dairy = get_object_or_404(MainDairy, id=main_dairy_id)
#     plans = SubscriptionPlan.objects.all()
#     # send public key to client (KEY_ID)
#     return render(request, 'mainapp/choose_plan.html', {
#         'main_dairy': main_dairy,
#         'plans': plans,
#         'razorpay_key_id': settings.RAZORPAY_KEY_ID
#     })

# # ---- activate free plan (no payment) ----
# @require_POST
# def activate_free_plan_view(request, main_dairy_id, plan_id):
#     main_dairy = get_object_or_404(MainDairy, id=main_dairy_id)
#     plan = get_object_or_404(SubscriptionPlan, id=plan_id)
#     if plan.plan_type != 'Free for 7 Days':
#         messages.error(request, "This is not a free plan.")
#         return redirect('choose_plan', main_dairy_id)

#     expiry = compute_expiry(plan.plan_type)
#     buy = BuySubscriptionPlan.objects.create(
#         main_dairy=main_dairy,
#         plan=plan,
#         amount=plan.price,
#         is_active=True,
#         expiry_date=expiry
#     )
#     main_dairy.current_plan = plan
#     main_dairy.expiry_date = expiry
#     main_dairy.save()

#     messages.success(request, "Free plan activated for 7 days.")
#     return redirect('home')


# # ---- create razorpay order (AJAX) ----
# @require_POST
# def create_razorpay_order(request):
#     try:
#         data = json.loads(request.body.decode('utf-8'))
#         plan_id = data.get('plan_id')
#         main_dairy_id = data.get('main_dairy_id')
#     except Exception as e:
#         return JsonResponse({"error": f"Invalid request: {str(e)}"}, status=400)
#     try:
    
#         plan = get_object_or_404(SubscriptionPlan, id=plan_id)
#         main_dairy = get_object_or_404(MainDairy, id=main_dairy_id)

#         amount_paise = int((plan.price * 100))
#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#         # client = razorpay.Client(auth=('rzp_test_sww6eyRpjsDm02', 'yVp1aHDQuoE4RRG5RMqjMmVG'))

#         receipt = f"md_{main_dairy.id}_p_{plan.id}_{int(timezone.now().timestamp())}"
#         order = client.order.create({
#             "amount": amount_paise,
#             "currency": "INR",
#             "receipt": receipt,
#             "payment_capture": 1
#         })

#         return JsonResponse({
#             "order_id": order.get('id'),
#             "amount": order.get('amount'),
#             "currency": order.get('currency'),
#             "key": settings.RAZORPAY_KEY_ID,
#             "plan_id": plan.id,
#             "main_dairy_id": main_dairy.id
#         })
        
#     except Exception as e:
#         return JsonResponse({"error": f"order request: {str(e)}"}, status=400)


# # ---- verify payment (AJAX POST) ----
# @require_POST
# def verify_payment(request):
#     try:
#         data = json.loads(request.body.decode('utf-8'))
#         razorpay_payment_id = data.get('razorpay_payment_id')
#         razorpay_order_id = data.get('razorpay_order_id')
#         razorpay_signature = data.get('razorpay_signature')
#         plan_id = data.get('plan_id')
#         main_dairy_id = data.get('main_dairy_id')
#     except Exception:
#         return JsonResponse({"success": False, "error": "Invalid payload"}, status=400)

#     client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

#     # verify signature
#     try:
#         client.utility.verify_payment_signature({
#             'razorpay_order_id': razorpay_order_id,
#             'razorpay_payment_id': razorpay_payment_id,
#             'razorpay_signature': razorpay_signature
#         })
#     except Exception as e:
#         return JsonResponse({"success": False, "error": "Signature verification failed"}, status=400)

#     # At this point payment is valid — save purchase
#     plan = get_object_or_404(SubscriptionPlan, id=plan_id)
#     main_dairy = get_object_or_404(MainDairy, id=main_dairy_id)
#     expiry = compute_expiry(plan.plan_type)

#     buy = BuySubscriptionPlan.objects.create(
#         main_dairy=main_dairy,
#         plan=plan,
#         razorpay_order_id=razorpay_order_id,
#         razorpay_payment_id=razorpay_payment_id,
#         amount=plan.price,
#         is_active=True,
#         expiry_date=expiry
#     )

#     main_dairy.current_plan = plan
#     main_dairy.expiry_date = expiry
#     main_dairy.save()

#     return JsonResponse({"success": True, "redirect_url": reverse('home')})





# def login_view(request):
#     if request.method == 'POST':
#         identifier = request.POST.get('username')  
#         password = request.POST.get('password')

#         user = User.objects.filter(
#             Q(username=identifier) |
#             Q(email=identifier) |
#             Q(mobile=identifier)
#         ).first()

#         if user:
#             user_auth = authenticate(request, username=user.username, password=password)
#             if user_auth:
#                 login(request, user_auth)               
#                 if user.role == 'Admin':
#                     dairy = Dairy.objects.get(user=user, role='Main')  # Main Dairy admin
#                     main_dairy = dairy.main_dairy

#                     if main_dairy.is_plan_expired():
#                         logout(request)

#                         messages.warning(request, "Your subscription plan has expired. Please purchase a plan to continue.")
#                         return redirect('purchase_plan')  # Replace with your plan purchase view name

#                 elif user.role in ['Customer', 'Manager']:
#                     dairy = request.user.dairy_profile.dairy
#                     main_dairy = dairy.main_dairy

#                     if main_dairy.is_plan_expired():
#                         logout(request)
#                         messages.warning(request, "Your main dairy's subscription has expired. Please contact the admin.")
#                         return redirect('home')  # Or wherever they should go
#                 return redirect('home')

#         messages.error(request, 'Invalid username, email, mobile, or password')
#         return redirect('login')

#     return render(request, 'mainapp/login.html')


######################################################################################### end with plan +++++++++++++


# Signup View
def signup_dairy_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        dairy_name = request.POST.get('dairy_name')
        profile_image = request.FILES.get('profile_image')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('signup')

        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already in use.")
            return redirect('signup')


        # Create User with profile image
        user = User.objects.create_user(
            username=username,
            first_name=username,
            email=email,
            password=password1,
            mobile=mobile,
            address=address,
            role='Admin',
            profile_image=profile_image
        )

        # Create Dairy and link profile
        main_dairy = MainDairy.objects.create(name=dairy_name)
        dairy = Dairy.objects.create(main_dairy = main_dairy,user=user, name=dairy_name,role = 'Main',is_main = True)
        DairyUserProfile.objects.create(user=user, dairy=dairy)

        login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect('home')

    return render(request, 'mainapp/signupmain_dairy.html')




# This could be email/mobile/username
def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username')  
        password = request.POST.get('password')

        # Try to find the user using email or mobile
        user = User.objects.filter(
            Q(username=identifier) |
            Q(email=identifier) |
            Q(mobile=identifier)
        ).first()

        if user:
            user_auth = authenticate(request, username=user.username, password=password)
            if user_auth:
                login(request, user_auth)
                return redirect('home')

        messages.error(request, 'Invalid username, email, mobile, or password')
        return redirect('login')

    return render(request, 'mainapp/login.html')



# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def update_profile_view(request):
    user = request.user
    if request.method == 'POST':
        name = request.POST.get('name') 
        address = request.POST.get('address')
        profile_image = request.FILES.get('profile_image')
        dairy_name = request.POST.get('dairy_name')


        if address:
            user.address = address
        if name:
            user.first_name = name

        if profile_image:
            user.profile_image = profile_image

        user.save()
        if user.role == 'Admin' and hasattr(user, 'dairy'):
            user.dairy.name = dairy_name
            user.dairy.save()


        return redirect('home')

    return render(request, 'mainapp/update_profile.html', {'user': user})








@login_required
def branch_dairy_list(request):
    if request.user.role not in ['Admin','Manager','SuperAdmin']:
        messages.error(request, "Unauthorized access.")
        return redirect('home')
    if request.user.role == 'SuperAdmin':
        branches = Dairy.objects.all()
        return render(request, 'mainapp/branch_dairy_list.html', {'dairies': branches})
    elif request.user.role == 'Admin':
        main_dairy = request.user.dairy.main_dairy
        branches = Dairy.objects.filter(main_dairy=main_dairy)
        return render(request, 'mainapp/branch_dairy_list.html', {'dairies': branches})
    else:
        dairy = request.user.dairy_profile
        print(dairy.dairy.id,'jkjkh')
        branches = Dairy.objects.filter(user = request.user)
        print(branches,'djkhjhh')
        return render(request, 'mainapp/branch_dairy_list.html', {'dairies': branches})

# Add new branch (admin only)
@login_required
def add_branch_dairy(request):
    if request.user.role != 'Admin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    main_dairy = request.user.dairy.main_dairy
    managers = DairyUserProfile.objects.filter(
        dairy__main_dairy=main_dairy,
        user__role='Manager'
    )

    if request.method == 'POST':
        branch_name = request.POST.get('dairy_name')
        manager_id = request.POST.get('manager_id')

        manager = User.objects.filter(id=manager_id, role='Manager').first()
        if not manager:
            messages.error(request, 'Manager not found.')
            return redirect('add_branch_dairy')

        dairy = Dairy.objects.create(
            user=manager,
            name=branch_name,
            role='Branch',
            main_dairy=main_dairy
        )

        messages.success(request, "Branch dairy created and manager assigned.")
        return redirect('branch_dairy_list')

    return render(request, 'mainapp/branch_dairy_form.html', {
        'managers': managers,
        'edit': False
    })

# Edit branch (admin only)
@login_required
def edit_branch_dairy(request, dairy_id):
    if request.user.role != 'Admin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    dairy =Dairy.objects.filter(id = dairy_id).first()
    manager =DairyUserProfile.objects.filter(user__role = 'Manager')
    print(manager,'manager')
    if not dairy:
        messages.success(request, "Branch id not found.")
        return render(request, 'mainapp/branch_dairy_list.html', {'dairy': dairy,'edit':True})


    if request.method == 'POST':
        dairy.name = request.POST.get('name')
        dairy.dairy_profile.user = request.POST.get('manager_id')
        
        
        dairy.save()
        messages.success(request, "Branch updated successfully.")
        return redirect('branch_dairy_list')

    return render(request, 'mainapp/branch_dairy_form.html', {'dairy': dairy,'edit':True,'manager':manager})

# Delete branch (admin only)
@login_required
def delete_branch_dairy(request, dairy_id):
    if request.user.role != 'Admin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    dairy =Dairy.objects.filter(id = dairy_id).first()
    if not dairy:
        messages.success(request, "Branch id not found.")
        return render(request, 'mainapp/branch_dairy_list.html', {'dairy': dairy})

    dairy.delete()
    messages.success(request, "Branch deleted.")
    return redirect('branch_dairy_list')






@login_required
def user_list_view(request):
    if request.user.role not in ['Admin', 'Manager']:
        messages.error(request, "Unauthorized access.")
        return redirect('home')
    dairies = None
    selected_dairy_id = None
    if request.user.role  == 'Manager':
        dairy = request.user.dairy if hasattr(request.user, 'dairy') else request.user.dairy_profile.dairy
        users = User.objects.filter(dairy_profile__dairy=dairy)
    if request.user.role  == 'Admin':
        selected_dairy_id = request.GET.get('dairy_id')      
        dairy = request.user.dairy if hasattr(request.user, 'dairy') else request.user.dairy_profile.dairy
        main_dairy = dairy.main_dairy
        dairies = Dairy.objects.filter(main_dairy=main_dairy)
        users = User.objects.filter(dairy_profile__dairy__in=dairies)
        if selected_dairy_id:
            users = User.objects.filter(dairy_profile__dairy__in=selected_dairy_id)
   
    return render(request, 'mainapp/user_list.html', {'users': users,'dairies': dairies,'selected_dairy_id': selected_dairy_id})


# Only Admins or Managers can access
@login_required
def add_user_view(request):
    if request.user.role not in ['Admin', 'Manager']:
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        role = request.POST.get('role')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        profile_image = request.FILES.get('profile_image')
       
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('add_user')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('add_user')

        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already in use.")
            return redirect('add_user')


        user = User.objects.create_user(
            username=username,
            first_name = username,
            email=email,
            password=password,
            mobile=mobile,
            address=address,
            role=role,
            profile_image=profile_image
        )

        # Assign to same dairy as logged-in user
        if hasattr(request.user, 'dairy'):
            dairy = request.user.dairy
        elif hasattr(request.user, 'dairyuserprofile'):
            dairy = request.user.dairyuserprofile.dairy
        else:
            messages.error(request, "Dairy not found for logged-in user.")
            return redirect('home')

        DairyUserProfile.objects.create(user=user, dairy=dairy)

        messages.success(request, f"{role} created and assigned to your dairy.")
        return redirect('home')

    return render(request, 'mainapp/add_user.html')



@login_required
def edit_user_view(request, pk):

    user = User.objects.filter( pk=pk).first()
    if not user:
        if not user:
            messages.error(request, "User not found.")
        return redirect('user_list')


    if request.method == 'POST':
        user.first_name = request.POST.get('username')
        user.email = request.POST.get('email')
        user.mobile = request.POST.get('mobile')
        user.address = request.POST.get('address')
        user.role = request.POST.get('role')
        
        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, "User updated successfully.")
        return redirect('user_list')

    return render(request, 'mainapp/add_user.html', {'edit': True, 'user_obj': user})


@login_required
def delete_user_view(request, pk):
    user = User.objects.filter( pk=pk).first()
    if not user:
        if not user:
            messages.error(request, "User not found.")
        return redirect('user_list')
    if user:
        user.delete()
        messages.success(request, "User deleted successfully.")
    return redirect('user_list')



@login_required
def milk_type_list(request):
    if request.user.role not in ['Admin', 'Manager']:
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    if request.user.role == 'Admin':
        selected_dairy_id = request.GET.get('dairy_id')      

        dairy = request.user.dairy if hasattr(request.user, 'dairy') else request.user.dairy_profile.dairy
        main_dairy = dairy.main_dairy
        dairies = Dairy.objects.filter(main_dairy=main_dairy)
        milk_types = MilkType.objects.filter(dairy__in=dairies)
        if selected_dairy_id:
            milk_types = MilkType.objects.filter(dairy__in=selected_dairy_id)
    else:
        dairy = request.user.dairy if hasattr(request.user, 'dairy') else request.user.dairy_profile.dairy
        milk_types = MilkType.objects.filter(dairy=dairy)
        dairies = None
        selected_dairy_id = None
        
    return render(request, 'mainapp/milk_type_list.html', {'milk_types': milk_types,'dairies': dairies,'selected_dairy_id': selected_dairy_id})


@login_required
def add_milk_type(request):
    if request.user.role not in ['Admin', 'Manager']:
        messages.error(request, "Unauthorized access")
        return redirect('home')

    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price_per_litre']

        if hasattr(request.user, 'dairy'):
            dairy = request.user.dairy
        else:
            dairy = request.user.dairy_profile.dairy

        MilkType.objects.create(dairy=dairy, name=name, price_per_litre=price)
        messages.success(request, "Milk Type added successfully")
        return redirect('/milk-type/')

    return render(request, 'mainapp/milk_type_form.html')


@login_required
def edit_milk_type(request, pk):
    milk_type = MilkType.objects.filter( pk=pk).first()
    if not milk_type:
        if not milk_type:
            messages.error(request, "Milk Type not found.")
        return redirect('milk_type_list')


    if request.method == 'POST':
        milk_type.name = request.POST['name']
        milk_type.price_per_litre = request.POST['price_per_litre']
        milk_type.save()
        messages.success(request, "Milk Type updated")
        return redirect('milk_type_list')

    return render(request, 'mainapp/milk_type_form.html', {'milk_type': milk_type, 'edit': True})


@login_required
def delete_milk_type(request, pk):
    milk_type = MilkType.objects.filter( pk=pk).first()
    if not milk_type:
        if not milk_type:
            messages.error(request, "Milk Type not found.")
        return redirect('milk_type_list')

    milk_type.delete()
    messages.success(request, "Milk Type deleted")
    return redirect('milk_type_list')


from django.db.models import Sum, Case, When, FloatField
from django.db.models import Q
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Sum, Case, When, FloatField, F
from django.utils import timezone
from django.contrib import messages
from .models import MilkCollection, Dairy, MilkType
from datetime import datetime
from django.utils import timezone
from django.views.decorators.http import require_POST

@login_required
def milk_collection_list(request):
    user = request.user
    customer = None
    selected_dairy_id = request.GET.get('dairy_id')
    customer_id = request.GET.get('customer_id')
    payment_status = request.GET.get('payment_status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    dairy = getattr(user, 'dairy', getattr(user, 'dairy_profile', None).dairy)

    if user.role == 'Admin':
        main_dairy = dairy.main_dairy
        dairies = Dairy.objects.filter(main_dairy=main_dairy)
        if selected_dairy_id:
            collections = MilkCollection.objects.filter(dairy__id=selected_dairy_id)
        else:
            collections = MilkCollection.objects.filter(dairy__in=dairies)
    elif user.role == 'Manager':
        dairies = [dairy]
        collections = MilkCollection.objects.filter(dairy=dairy)
        customer = DairyUserProfile.objects.filter(dairy=request.user.dairy_profile.dairy,user__role = 'Customer')
        if customer_id:
            collections = MilkCollection.objects.filter(userprofile = customer_id)
        
    else:
        dairies = [dairy]
        collections = MilkCollection.objects.filter(userprofile=request.user.dairy_profile.id)
        
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        collections = collections.filter(collection_date__range=(start, end))
    
    if payment_status == 'Paid':
        collections = collections.filter(is_paid=True)
    elif payment_status == 'Unpaid':
        collections = collections.filter(is_paid=False)

    collections = collections.order_by('-id')

    totals = collections.values('milk_type').annotate(
        total=Sum('quantity'),
        total_sale=Sum(Case(When(type='Sale', then='quantity'), output_field=FloatField())),
        total_purchase=Sum(Case(When(type='Purchase', then='quantity'), output_field=FloatField()))).order_by('milk_type')
    
    
    amount_summary = collections.aggregate(
        purchase_total=Sum(Case(When(type='Purchase', then='amount'), output_field=FloatField())),
        purchase_paid=Sum(Case(When(Q(type='Purchase') & Q(is_paid=True), then='amount'), output_field=FloatField())),
        purchase_unpaid=Sum(Case(When(Q(type='Purchase') & Q(is_paid=False), then='amount'), output_field=FloatField())),
        sale_total=Sum(Case(When(type='Sale', then='amount'), output_field=FloatField())),
        sale_paid=Sum(Case(When(Q(type='Sale') & Q(is_paid=True), then='amount'), output_field=FloatField())),
        sale_unpaid=Sum(Case(When(Q(type='Sale') & Q(is_paid=False), then='amount'), output_field=FloatField())),
    )
    print(customer_id,'jdkfdkgjj')
    return render(request, 'mainapp/milk_collection_list.html', {
        'collections': collections,
        'totals': totals,
        'start_date': start_date,
        'end_date': end_date,
        'dairies': dairies,
        'customer': customer,
        'customer_id':customer_id,
        'selected_dairy_id': selected_dairy_id,
        'payment_status': payment_status,
        'amount_summary': amount_summary

    })





# @login_required
# @require_POST
# def update_payment_status(request):
    ids = request.POST.getlist('collection_ids')
    action = request.POST.get('action')

    if not ids:
        messages.warning(request, "No entries selected.")
        return redirect('milk_collection_list')

    if action == 'mark_paid':
        MilkCollection.objects.filter(id__in=ids).update(is_paid=True, payment_date=timezone.now())
        # collection = PaymentHistory.objects.create(
        #             collection=collection,
        #             amount=collection.amount,
        #             status="Paid"
        #         )
        messages.success(request, "Selected entries marked as Paid.")
    elif action == 'mark_unpaid':
        collection = MilkCollection.objects.filter(id__in=ids).update(is_paid=False, payment_date=None)
        # collection = PaymentHistory.objects.create(
        #             collection=collection,
        #             amount=collection.amount,
        #             status="Paid"
        #         )
        messages.success(request, "Selected entries marked as Unpaid.")
    else:
        messages.error(request, "Invalid action.")

    return redirect('milk_collection_list')





@login_required
@require_POST
def update_payment_status(request):
    ids = request.POST.getlist('collection_ids')
    action = request.POST.get('action')

    if not ids:
        messages.warning(request, "No entries selected.")
        return redirect('milk_collection_list')

    # Retrieve the collections to be updated
    collections = MilkCollection.objects.filter(id__in=ids)

    if action == 'mark_paid':
        # Update collections to mark as paid
        collections.update(is_paid=True, payment_date=timezone.now())

        # Create PaymentHistory entries for each collection
        for collection in collections:
            PaymentHistory.objects.create(
                collection=collection,
                amount=collection.amount,
                status="Paid",
                payment_date=timezone.now()
            )

        messages.success(request, "Selected entries marked as Paid.")
    elif action == 'mark_unpaid':
        collections.update(is_paid=False, payment_date=None)

        for collection in collections:
            PaymentHistory.objects.create(
                collection=collection,
                amount=collection.amount,
                status="Unpaid",
                payment_date=None
            )

        messages.success(request, "Selected entries marked as Unpaid.")
    else:
        messages.error(request, "Invalid action.")

    return redirect('milk_collection_list')



from django.shortcuts import render
from .models import PaymentHistory
from django.utils import timezone
@login_required
def payment_history(request):
    user = request.user
    dairy = getattr(user, 'dairy', getattr(user, 'dairy_profile', None).dairy)

    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    status = request.GET.get('status', '')

    if user.role == 'Admin':
        main_dairy = dairy.main_dairy
        dairies = Dairy.objects.filter(main_dairy=main_dairy)
        payment_history = PaymentHistory.objects.filter(collection__dairy__in = dairies)

    elif user.role == 'Manager':
        dairies = [dairy]
        payment_history = PaymentHistory.objects.filter(collection__dairy = dairy)

    else:
        dairies = [dairy]
        payment_history = PaymentHistory.objects.filter(collection__userprofile=request.user.dairy_profile.id)

    if start_date:
        payment_history = payment_history.filter(payment_date__gte=start_date)
    if end_date:
        payment_history = payment_history.filter(payment_date__lte=end_date)
    if status:
        payment_history = payment_history.filter(status=status)

    return render(request, 'mainapp/payment_history.html', {
        'payment_history': payment_history,
        'start_date': start_date,
        'end_date': end_date,
        'status': status
    })


@login_required
def milk_collection_add(request):
    if request.user.role not in ['Admin', 'Manager']:
        messages.error(request, "Unauthorized")
        return redirect('home')

    dairy = request.user.dairy if hasattr(request.user, 'dairy') else request.user.dairy_profile.dairy
    customers = DairyUserProfile.objects.filter(dairy=dairy, user__role='Customer')
    milk_types = MilkType.objects.filter(dairy=dairy)

    if request.method == 'POST':
        userprofile_id = request.POST.get('userprofile_id')
        milk_type_name = request.POST.get('milk_type')
        quantity = float(request.POST.get('quantity'))

        userprofile = DairyUserProfile.objects.get(id=userprofile_id)
        milk_type_obj = MilkType.objects.get(dairy=dairy, name=milk_type_name)
        amount = float(milk_type_obj.price_per_litre) * quantity

        MilkCollection.objects.create(
            dairy=dairy,
            milk_type=milk_type_name,
            quantity=quantity,
            type='Purchase',
            userprofile=userprofile,
            amount=amount
        )

        stock, created = MilkStock.objects.get_or_create(dairy=dairy, milk_type=milk_type_name)
        stock.quantity = (stock.quantity or 0) + quantity
        stock.save()

        messages.success(request, f"{quantity}L {milk_type_name} collected for ₹{amount:.2f}.")
        return redirect('milk_collection_list')

    return render(request, 'mainapp/milk_collection_form.html', {
        'customers': customers,
        'milk_types': milk_types
    })


@login_required
def edit_milk_collection(request, pk):
    collection = MilkCollection.objects.filter(pk=pk).first()
    if not collection:
        messages.error(request, "Milk collection not found.")
        return redirect('milk_collection_list')

    dairy = collection.dairy
    customers = DairyUserProfile.objects.filter(dairy=dairy, user__role='Customer')
    milk_types = MilkType.objects.filter(dairy=dairy)

    if request.method == 'POST':
        milk_type_name = request.POST.get('milk_type')
        quantity = float(request.POST.get('quantity'))
        userprofile_id = request.POST.get('userprofile_id')

        milk_type_obj = MilkType.objects.get(dairy=dairy, name=milk_type_name)
        amount = float(milk_type_obj.price_per_litre) * quantity

        collection.milk_type = milk_type_name
        collection.quantity = quantity
        collection.amount = amount
        collection.userprofile = DairyUserProfile.objects.get(id=userprofile_id)
        collection.save()

        messages.success(request, "Milk collection updated.")
        return redirect('milk_collection_list')

    return render(request, 'mainapp/milk_collection_form.html', {
        'edit': True,
        'collection': collection,
        'customers': customers,
        'milk_types': milk_types
    })

@login_required
def delete_milk_collection(request, pk):
    collection = MilkCollection.objects.filter(pk=pk).first()
    if not collection:
        messages.error(request, "Milk collection not found.")
    else:
        collection.delete()
        messages.success(request, "Milk collection deleted.")
    return redirect('milk_collection_list')



@login_required
def milk_sale_add(request):
    if request.user.role not in ['Admin', 'Manager']:
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    dairy = request.user.dairy if hasattr(request.user, 'dairy') else request.user.dairy_profile.dairy

    customers = DairyUserProfile.objects.filter(dairy=dairy, user__role='Customer')
    milk_types = MilkType.objects.filter(dairy=dairy)

    if request.method == 'POST':
        userprofile_id = request.POST.get('userprofile_id')
        milk_type = request.POST.get('milk_type')
        quantity = float(request.POST.get('quantity'))

        stock = MilkStock.objects.filter(dairy=dairy, milk_type=milk_type).first()

        if not stock or stock.quantity is None or stock.quantity < quantity:
            messages.error(request, f"Not enough stock for {milk_type}. Available: {stock.quantity if stock else 0}L")
            return redirect('milk_sale')

        userprofile = DairyUserProfile.objects.get(id=userprofile_id)

        milk_type_obj = MilkType.objects.get(dairy=dairy, name=milk_type)
        amount = float(milk_type_obj.price_per_litre) * quantity

        MilkCollection.objects.create(
            dairy=dairy,
            milk_type=milk_type,
            quantity=quantity,
            type='Sale',
            userprofile=userprofile,
            amount = amount
        )

        # Update stock (reduce)
        stock.quantity -= quantity
        stock.save()

        messages.success(request, f"{quantity}L {milk_type} sold and stock updated.")
        return redirect('milk_collection_list')

    return render(request, 'mainapp/milk_sale_form.html', {
        'customers': customers,
        'milk_types': milk_types
    })


from collections import defaultdict
from django.db.models import Sum




@login_required
def milk_stock_view(request):
    if request.user.role not in ['Admin', 'Manager']:
        messages.error(request, "Unauthorized")
        return redirect('home')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if request.user.role == 'Admin':
        selected_dairy_id = request.GET.get('dairy_id')
        
        main_dairy = request.user.dairy.main_dairy
        dairies = Dairy.objects.filter(main_dairy=main_dairy)
        stocks = MilkStock.objects.filter(dairy__in=dairies)
        
        if selected_dairy_id:
            stocks = MilkStock.objects.filter(dairy__in=selected_dairy_id)
    
    else:
        dairy = request.user.dairy if hasattr(request.user, 'dairy') else request.user.dairy_profile.dairy
        stocks = MilkStock.objects.filter(dairy=dairy)
        dairies = None
        selected_dairy_id = None
    if start_date and end_date:
        stocks = MilkStock.objects.filter(updated_at__range=[start_date, end_date])


    # Group summary
    summary = defaultdict(dict)
    for stock in stocks:
        branch_name = stock.dairy.name
        milk_name = stock.milk_type
        summary[branch_name][milk_name] = stock.quantity

    return render(request, 'mainapp/milk_stock_list.html', {
        'stocks': stocks,
        'summary': dict(summary),
        'dairies' : dairies,
        'start_date': start_date,
        'end_date': end_date,
        'selected_dairy_id': selected_dairy_id
        
    })
