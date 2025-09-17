from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages

### superAdmin

# @login_required
def subscription_plan_list(request):
    # if request.user.role != 'SuperAdmin':
    #     messages.error(request, "Unauthorized access.")
    #     return redirect('home')
    plans = SubscriptionPlan.objects.all()
    return render(request, 'mainapp/subscription_plan_list.html', {'plans': plans})

# Add plan
@login_required
def add_subscription_plan(request):
    if request.user.role != 'SuperAdmin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')
   

    plan_choices = SubscriptionPlan.PLAN_CHOICES
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        number_of_sub_dairy = request.POST.get('number_of_sub_dairy')
        plan_type = request.POST.get('plan_type')
        description = request.POST.get('description')
        if SubscriptionPlan.objects.filter(plan_type = plan_type).exists():
            messages.success(request, "Subscription Already exists")
            return render(request, 'mainapp/subscription_plan_form.html', {'edit': False,'plan_choices':plan_choices})
            
        SubscriptionPlan.objects.create(
            name=name,
            price=price,
            plan_type=plan_type,
            number_of_sub_dairy = number_of_sub_dairy,
            description=description
        )
        messages.success(request, "Subscription plan created successfully.")
        return redirect('subscription_plan_list')

    return render(request, 'mainapp/subscription_plan_form.html', {'edit': False,'plan_choices':plan_choices})

# Edit plan
@login_required
def edit_subscription_plan(request, plan_id):
    print(plan_id,'smkfmsdk')
    if request.user.role != 'SuperAdmin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    plan_choices = SubscriptionPlan.PLAN_CHOICES
    if SubscriptionPlan.objects.filter(plan_type = request.POST.get('plan_type')).exclude(id = plan.id).exists():
        messages.success(request, "Subscription Already exists")
        return render(request, 'mainapp/subscription_plan_form.html', {'plan': plan, 'edit': True,'plan_choices':plan_choices})
            
    if request.method == 'POST':
        plan.name = request.POST.get('name')
        plan.price = request.POST.get('price')
        plan.plan_type = request.POST.get('plan_type')
        plan.number_of_sub_dairy = request.POST.get('number_of_sub_dairy')
        plan.description = request.POST.get('description')
        plan.save()
        messages.success(request, "Subscription plan updated successfully.")
        return redirect('subscription_plan_list')

    return render(request, 'mainapp/subscription_plan_form.html', {'plan': plan, 'edit': True,'plan_choices':plan_choices})

# Delete plan
@login_required
def delete_subscription_plan(request, plan_id):
    if request.user.role != 'SuperAdmin':
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    plan.delete()
    messages.success(request, "Subscription plan deleted successfully.")
    return redirect('subscription_plan_list')

