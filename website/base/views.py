import os, re, random, json, datetime
from datetime import timedelta, date
from django.utils import timezone

import psutil
import re
import socket
from datetime import timedelta, datetime, date
import csv
import string

from smtplib import SMTPException
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from allauth.account.views import SignupView, LoginView
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseRedirect

from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.contrib.auth import authenticate, login
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.contrib.auth.models import User as U
# from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _


from django.contrib.sites.models import Site
from responder.models import (
        Gateway,
        AddGateway,
        AssignContact,
        Admin,
        Ani,
        AssignedAni,
        CronJob,
        InOutSms,
        UserPassword,
        PrimaryNumber,
        Css
    )
from .models import (
        Messenger,
        Support,
        Contact,
        Chat,
        ShortenedUrl
    )
from facebook.models import AdForm, FacebookLead

User = get_user_model()



def visit_real_url(request, short_url):
    if request.method == "GET":
        real_urls = ShortenedUrl.objects.filter(hash_code=short_url.strip())
        if real_urls:
            return HttpResponseRedirect(real_urls[0].given_url)
    return HttpResponse(status=400)


def hash_generator(size=9, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def shortened_url(request):

    if request.method == 'GET':
        urls = ShortenedUrl.objects.filter(admin__admin=request.user)
        if urls:
            urls = list(urls.values())
        else:
            urls = ''

        data = {
            'urls': urls
        }
        return JsonResponse(data=data, status=200)

    if request.is_ajax():
        data = json.loads(request.body)
        check = data['check']
        if check =="shorten_url":
            given_url = data.get("given_url")

            while True:
                hash_code = hash_generator()
                print(hash_code)
                if not ShortenedUrl.objects.filter(hash_code=hash_code).exists():
                    domain = Site.objects.all()[0].domain
                    shortened_url = domain + '/' + hash_code
                    break
                else:
                    continue

            if hash_code:
                admin_obj = get_object_or_404(Admin, admin=request.user)

                ShortenedUrl.objects.create(
                    admin = admin_obj,
                    hash_code = hash_code,
                    given_url = given_url,
                    shortened_url = shortened_url
                )

            return JsonResponse(data=data, status=200)

        elif check == "get_url":
            url_id = data.get("url_id")

            url = list(ShortenedUrl.objects.filter(id=url_id).values())[0]

            data = {
                'url': url
            }

            return JsonResponse(data=data, status=200)

        elif check == "update_url":
            url = data.get('url')
            url_id = url.get("id")
            given_url = url.get("given_url")
            
            ShortenedUrl.objects.filter(id=url_id).update(given_url=given_url)
            
            data = {

            }

            return JsonResponse(data=data, status=200)

        elif check == "delete_url":
            url_id = data.get("url_id")
            ShortenedUrl.objects.filter(id=url_id).delete()

            data = {

            }

            return JsonResponse(data=data, status=200)

def edit_ani_view(request, ani_id, admin_id):
    
    assigned_anis = ''

    if request.method == "POST":
        name = request.POST.get('name')
        ani = request.POST.get('phone')
        gateway_id = request.POST.get("gateway_id")
        admin_ids = request.POST.getlist('admin_id')
        print(admin_ids)

        Ani.objects.filter(id=ani_id).update(

                name = name,
                gateway_id = gateway_id,
                ani = ani
            )
        if admin_ids:
            objs = AssignedAni.objects.filter(ani_id=ani_id)
            if objs:
                print("ysssssss")
                objs.delete()
            for admin_id in admin_ids:
                AssignedAni.objects.create(
                        ani_id = ani_id,
                        admin_id = admin_id
                    
                    )
        return redirect('base:ani')

    ani = Ani.objects.filter(id=ani_id)[0]
    users = Admin.objects.all()
    if users:
        admin_ids = AssignedAni.objects.filter(ani_id=ani_id)
        assigned_admins = []
        for item in admin_ids:
            assigned_admins.append(item.admin_id)
            print(assigned_admins)
            users = users.exclude(admin_id__in=assigned_admins)
            print(users)

    gateways = AddGateway.objects.all()
    assigned_anis = AssignedAni.objects.filter(ani_id=ani_id)
    
    context = {
        'ani':ani,
        'assigned_anis':assigned_anis,
        # 'assigned_contact':assigned_contact,
        'users': users,
        'gateways': gateways
    }
    return render(request, 'base/edit_ani.html', context)

def ani_view(request):
    if request.user.is_superuser:
        gateways = AddGateway.objects.all()
        if request.is_ajax():
            data = json.loads(request.body)
            check = data.get("check")
            if check == "remove_ani":
                ani_ids = data.get("ani_ids")
                Ani.objects.filter(id__in=ani_ids).delete()

        elif request.method == "POST" and not request.is_ajax():
            name = request.POST.get("name")
            ani = request.POST.get("phone")
            gateway_id = request.POST.get("gateway_id")
            admin = get_object_or_404(Admin, admin=request.user)
            Ani.objects.create(
                    name = name,
                    gateway_id = gateway_id,
                    admin = admin,
                    ani = ani
                )
            return redirect(reverse("base:ani"))

        context = {
            'gateways': gateways
        }
        return render(request, 'base/ani.html', context)

def clear_media():
    """
    Cleared all media files while formatting db
    """
    from pathlib import Path
    import glob, os


    BASE_DIR = Path(__file__).resolve().parent.parent

    path = os.path.join(BASE_DIR, "media/gallery/")
    files = glob.glob("{}*".format(path))
    for path in files:
        os.remove(path)

@login_required
def support_chat(request, args):
    admin = ""
    user = ""
    if request.method == "POST":
        check = request.POST.get("check")
        if check == "send" or check == "received":
            received = request.POST.get("received")
            sent = request.POST.get("sent")
            admin_obj = get_object_or_404(User, username = args)
            Chat.objects.create(admin=admin_obj, sent=sent, received=received)
        elif check == "create":
            user = request.POST.get("user")
            Chat.objects.filter(admin__username=user).update(is_created=True)

    if request.user.is_superuser or request.user.is_staff:
        admin = args
    else:
        admin = request.user
    chats = Chat.objects.filter(admin__username = admin)
    if chats:
        user = chats[0].admin

    context = {
        "chats":chats,
        "user": user,
    }

    if request.is_ajax() and request.method=='POST':
        pass

    return render(request, 'base/chats.html', context)

def support_view(request):
    alert = ""
    messangers = ""
    ticket_created = False
    try:
        messangers = Messenger.objects.all()
    except:
        pass
    try:
        ticket_created = Chat.objects.filter(admin=request.user,is_created=True).exists()
    except:
        pass
    if request.method == "POST":
        check = request.POST['check']
        if check == "support":
            msg_id = request.POST['messanger']
            messanger_id = request.POST['messanger_id']
            subject = request.POST['subject']
            message = request.POST['message']
            msg_obj = get_object_or_404(Messenger, id=msg_id)
            try:
                Support.objects.create(user=request.user, messenger=msg_obj, subject=subject,message=message,msgr_id=messanger_id)
                admin_obj = get_object_or_404(User, username=request.user)
                Chat.objects.create(admin = admin_obj, received=message)
                alert = "Ticket created Succesfully"
            except:
                error = 'Something went wrong'
                pass

    context = {
        "alert":alert,
        "messangers":messangers,
        "ticket_created":ticket_created
    }
    return render(request, 'base/support.html', context)

@login_required
def admin_support_view(request):
    support = ""
    alert = ""
    error = ""
    if request.method =="POST":
        check = request.POST['check']
        if check == 'delete':
            support_id = request.POST['support_id']
            try:
                user_id = Support.objects.filter(id=support_id)[0].user_id
                Chat.objects.filter(admin_id=user_id).delete()
                Support.objects.filter(id=support_id).delete()
                alert = "Deleted Succesfully"
            except:
                error = "Something went wrong"
        elif check == "chat":
            admin = request.POST['admin']

            return redirect("base:support_ticket", admin)
        elif check == 'close':
            support_id = request.POST['support_id']
            try:
                Support.objects.filter(id=support_id).update(is_close=True)
                alert = "Ticket is closed"
            except:
                error = "Something went wrong"
    try:
        supports = Support.objects.all()
        # total_ticket = len()
        page = request.GET.get('page', 1)
        paginator = Paginator(supports, 10)
        try:
            supports = paginator.page(page)
        except PageNotAnInteger:
            supports = paginator.page(1)
        except EmptyPage:
            supports = paginator.page(paginator.num_pages)
    except:
        pass
    context = {
        'pages':supports,
        'alert':alert,
        'error':error,
    }

    return render(request, 'base/admin_support.html',context)

@login_required
def admin_report_view(request):
    """
    """

    alert = ""
    error = ""
    pages = ""
    if not request.user.is_superuser:
        return redirect('base:home')
    campaigns = Campaign.objects.all().annotate(lead_count=Count("inoutsms", filter=\
            Q(inoutsms__is_lead=True)))
    if request.method == "POST":
        check = request.POST['check']
        user = Admin.objects.filter(admin__username=request.user)[0]
        if check == "lead_check":
            day = request.POST['day']
            from django.utils import timezone
            # time = timezone.now() - timedelta(days=int(day),hours=0, minutes=0, seconds=0)
            time = timezone.now() - timedelta(days=0,hours=1, minutes=0, seconds=0)
            campaigns = Campaign.objects.all().annotate(lead_count=Count("inoutsms", filter=\
            Q(inoutsms__is_lead=True, timestamp__lte=time)))
        elif check == "search":
            user = request.POST['user']
            campaigns = Campaign.objects.filter(admin__admin__username__contains=user).\
            annotate(lead_count=Count("inoutsms", filter=Q(inoutsms__is_lead=True,)))

        elif check == "upload":
            file = ""
            try:
                file = request.FILES['lead']
            except:
                pass
            if file:
                admin_id = request.POST['admin_id']
                cam_id = request.POST['cam_id']
                cam = Campaign.objects.filter(admin_id=admin_id, id=cam_id)[0]
                cam.file = file
                cam.save()
                Admin.objects.filter(id=admin_id).update(file_attached=True)

                alert = "File Uploaded"
            else:
                error = "No file selected!"        
        elif check == "delete":
            files = ""
            admin_id = request.POST['admin_id']
            cam_id = request.POST['cam_id']
            try:
                files = Campaign.objects.filter(admin_id=admin_id, id=cam_id)
            except:
                pass
            if files:
                for file in files:
                    try:
                        path = file.file.path
                        os.remove(path)
                    except Exception as e:
                        print(e)
                files.update(file="")
                Admin.objects.filter(id=admin_id).update(file_attached=False)
                alert = "File Deleted"
            else:
                error = 'File not found!'
        elif check == "csv":
            if request.user.is_superuser or user.is_export:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="lead.csv"'
                writer = csv.writer(response)
                writer.writerow(['Dnis',])
                cam_id = request.POST['cam_id']
                dniss = InOutSms.objects.filter(admin__admin=request.user, campaign_id=cam_id,is_lead=True).values("dnis")
                for item in dniss:
                    dnis = item['dnis']
                    writer.writerow([dnis,])

                return response
        elif check == "txt":
            if request.user.is_superuser or user.is_export:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="lead.txt"'
                writer = csv.writer(response)
                cam_id = request.POST['cam_id']
                dniss = InOutSms.objects.filter(admin__admin=request.user, campaign_id=cam_id,is_lead=True).values("dnis")
                for item in dniss:
                    dnis = item['dnis']
                    writer.writerow([dnis,])

                return response
        elif check == "full_txt":
            if request.user.is_superuser or user.is_export:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="lead.txt"'
                writer = csv.writer(response)
                dniss = InOutSms.objects.filter(is_lead=True).values("dnis")
                for item in dniss:
                    dnis = item['dnis']
                    writer.writerow([dnis,])

                return response
        elif check == "full_csv":
            if request.user.is_superuser or user.is_export:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="lead.csv"'
                writer = csv.writer(response)
                writer.writerow(['Dnis',])
                dniss = InOutSms.objects.filter(is_lead=True).values("dnis")
                for item in dniss:
                    dnis = item['dnis']
                    writer.writerow([dnis,])

                return response
            else:
                error = "Export Error"
    if campaigns:
        page = request.GET.get('page', 1)
        paginator = Paginator(campaigns, 15)
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
    context = {
        "pages":pages,
        "alert":alert,
        "error":error
    }
    return render(request, 'responder/control-panel/report.html', context)

@login_required
def create_role_subadmin(request):
    is_access = False
    is_gateway = False
    is_chat = False
    is_import = False
    is_export = False
    alert = ""
    error = ""
    if request.method == 'POST':
        check = request.POST['check']
        if check == 'create_role':
            try:
                is_access = request.POST['limit']
                if is_access == 'on':
                    is_access = True
            except:
                pass    
            try:
                is_gateway = request.POST['gateway']
                if is_gateway == 'on':
                    is_gateway = True
            except:
                pass    
            try:
                is_chat = request.POST['chat']
                if is_chat == 'on':
                    is_chat = True
            except:
                pass  
            try:
                is_export = request.POST['export']
                if is_export == 'on':
                    is_export = True
            except:
                pass
            try:
                is_import = request.POST['bulk']
                if is_import == 'on':
                    is_import = True
            except:
                pass
            try:
                admin_id = request.POST['id']
                Admin.objects.filter(id=admin_id).update(is_limit=is_access, is_gateway=is_gateway,\
                is_dnis=is_chat, is_export=is_export,is_bulk=is_import)
                alert = "Role created"
            except Exception as e:
                print(e)    

    try:
        sub_users = Admin.objects.filter(is_subadmin=True).exclude(is_admin=True)
        page = request.GET.get('page', 1)
        paginator = Paginator(sub_users, 15)
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
    except:
        pass
    context = {
        "pages":pages,
        "alert": alert,
        "error":error,
    
    }
    return render(request, 'responder/control-panel/create-role-subadmin.html', context)

@login_required
def staff_view(request):
    context = {

    }
    return render(request, 'base/staff.html', context)

@login_required
def support_detail_view(request, id):
    support = ''
    try:
        support = Support.objects.get(id=id)
    except:
        pass
    context = {
        'support': support
    }
    return render(request, 'base/support_details.html', context)

@login_required
def create_user_view(request):
    
    if request.user.is_superuser:
        alert = ""
        error = ""
        if request.method == "POST":
            check = request.POST['check']
            if check == "create-user":
                user = request.POST['user']
                password = request.POST['password']
                if not User.objects.filter(username=user).exists():
                    User.objects.create_user(username=user, email=None, password=password)
                    user_obj = get_object_or_404(User, username=user)
                    Admin.objects.create(admin=user_obj, is_permitted=True)
                    alert = "User Created Succesfully"
                else:
                    error = "User already exists"
            elif check == "manage-user":
                print(request.POST)
    else:
        error = "Permission Denied"

    context = {
        "alert":alert,
        "error":error,
    }

    return render(request, 'base/create-user.html', context)
@login_required
def add_member_view(request):
    user_results  = ""
    search_count  = ""
    alert = ""
    error = ""
    try:
        user_results = User.objects.all().order_by('-date_joined')
    except Exception as e:
        print(e)
    if request.user.is_superuser:
        if request.method == "POST":
            check = request.POST['check']
            if check == "remove":
                admin = request.POST["user_name"]
                Admin.objects.filter(admin__username=admin).delete()
                User.objects.filter(username=admin)[0].delete()
                alert = 'User Removed !'
            elif check == "search_users":
                user_search = request.POST["user_search"]
                user_results = User.objects.filter(username__contains=user_search).order_by('-date_joined')
                if not user_results:
                    user_results = User.objects.filter(email__contains=user_search).order_by('-date_joined')
                search_count = len(user_results)
            elif check == "add":
                user_name = request.POST["user_name"]
                if not Admin.objects.filter(admin__username=user_name).exists():
                    user_obj = get_object_or_404(User, username=user_name)
                    Admin.objects.create(admin=user_obj, is_permitted=True)
                    alert = "User added Succesfully"
                else:
                    error = "User already exists !"
            else:
                pass 
    else:
        pass

    context = {
        "search_results": user_results,
        "count": search_count,
        'alert':alert,
        "error":error,
    }

    return render(request, 'responder/control-panel/member.html', context)

def create_role_view(request):
    users = ""
    is_lead = False
    is_response = False
    is_link = False
    is_delivered = False
    is_undelivered = False
    is_bulk = False
    is_ani = False
    is_export = False
    is_dnis = False
    is_campaign = False
    is_gateway = False
    search = False
    alert = ""
    error = ""
    if request.user.is_superuser or request.user.is_staff:
        if request.method == "POST":
            check = request.POST['check']
            if check == "create_role":
                try:
                    is_lead = request.POST['lead']
                    if is_lead == 'on':
                        is_lead = True
                except:
                    pass			
                try:
                    is_response = request.POST['response']
                    if is_response == "on":
                        is_response = True
                except:
                    pass			
                try:
                    is_link = request.POST['links']
                    if is_link == "on":
                        is_link = True
                except:
                    pass			
                try:
                    is_delivered = request.POST['delivered']
                    if is_delivered == "on":
                        is_delivered = True
                except:
                    pass			
                try:
                    is_undelivered = request.POST['undelivered']
                    if is_undelivered == "on":
                        is_undelivered = True
                except:
                    pass			
                try:
                    is_bulk = request.POST['bulk-sms']
                    if is_bulk == "on":
                        is_bulk = True
                except:
                    pass			
                try:
                    is_ani = request.POST['ani']
                    if is_ani == "on":
                        is_ani = True
                except:
                    pass	
                try:
                    is_campaign = request.POST['campaign']
                    if is_campaign == "on":
                        is_campaign = True
                except:
                    pass	
                try:
                    is_export = request.POST['export']
                    if is_export == "on":
                        is_export = True
                except:
                    pass
                try:
                    is_dnis = request.POST['dnis']
                    if is_dnis == "on":
                        is_dnis = True
                except:
                    pass                
                try:
                    is_gateway = request.POST['gateway']
                    if is_gateway == "on":
                        is_gateway = True
                except:
                    pass
                user = request.POST['id']
                Admin.objects.filter(admin__username=user).update(is_lead=is_lead,is_response=is_response,\
                    is_ani=is_ani,is_link=is_link,is_delivered=is_delivered,is_undelivered=is_undelivered,\
                    is_bulk=is_bulk,is_export=is_export,is_dnis=is_dnis,is_campaign=is_campaign,\
                    is_gateway=is_gateway)
                alert = "Permission Granted."
                context = {
                    "alert": alert,
                }
                # return redirect("base:super_admin")

            elif check == "search-member":
                user = request.POST['member'].strip()
                users = Admin.objects.filter(admin__username__contains=user)
                page = request.GET.get('page', 1)
                paginator = Paginator(users, 15)
                try:
                    pages = paginator.page(page)
                except PageNotAnInteger:
                    pages = paginator.page(1)
                except EmptyPage:
                    pages = paginator.page(paginator.num_pages)
                search = True

        try:
            if not search:
                # here admin is super and subadmin is admin
                if request.user.is_superuser:
                    users = Admin.objects.all().order_by("-id")
                elif request.user.is_staff:
                    users = Admin.objects.filter(is_admin=False, is_subadmin=False).order_by("-id")
                page = request.GET.get('page', 1)
                paginator = Paginator(users, 15)
                try:
                    pages = paginator.page(page)
                except PageNotAnInteger:
                    pages = paginator.page(1)
                except EmptyPage:
                    pages = paginator.page(paginator.num_pages)
        except:
            pass
    else:
        return redirect("base:home")
    context = {
        'pages':pages,
        "alert":alert,
        "error":error,
    }
    return render(request, 'responder/control-panel/create-role.html', context)


@login_required
def settings_view(request):
    cronjobs = ""
    alert = False

    if request.method == "POST":
        if request.user.is_superuser:
            check = request.POST['check']
            if check == "cronjob":
                admin_obj = ""
                url = request.POST['url']
                # print(url)
                try:
                    admin_obj = get_object_or_404(User, username=request.user)
                except Exception as e:
                    print(e)
                CronJob.objects.create(admin=admin_obj, cron_job=url)
                alert = "Added Succesfully!"
            if check == "delete":
                cron_id = request.POST['id']
                CronJob.objects.get(id=cron_id).delete()
                alert = "Deleted Succesfully!"
        else:
            alert = "Permission Denied"
    try:
        cronjobs = CronJob.objects.all()
    except:
        pass

    context = {
        "cronjobs": cronjobs,
        "alert":alert,

    }
    return render(request, 'settings/settings.html', context)

@login_required
def access_view(request):

    if request.user.is_superuser:
        users = ""
        f_error = ""
        alert = None
        error = None
        username = ""
        subusers = ""
        sub_error = ""
        try:
            users = User.objects.all()
            page = request.GET.get('page', 1)
            paginator = Paginator(users, 10)
            try:
                users = paginator.page(page)
            except PageNotAnInteger:
                users = paginator.page(1)
            except EmptyPage:
                users = paginator.page(paginator.num_pages)
        except:
            pass
        try:
            subusers = Admin.objects.all()
            page = request.GET.get('page', 1)
            paginator = Paginator(subusers, 10)
            try:
                subusers = paginator.page(page)
            except PageNotAnInteger:
                subusers = paginator.page(1)
            except EmptyPage:
                subusers = paginator.page(paginator.num_pages)
        except:
            pass

        if request.method == "POST":
            check = request.POST["check"]
            if check == "search-users":
                username = request.POST["username"]
                users = User.objects.filter(username__contains=username)
                if not users:
                    f_error = "No result found."

            elif check == "login":
                username = request.POST['username']
                password = request.POST['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request,user)
                    alert = "Login Succesfull"
                else:
                    error = "incorrect user or password!"
            elif check == "search-for-subadmin":
                username = request.POST['username']
                subusers = Admin.objects.filter(admin__username__contains=username)
                if not subusers.exists():
                    sub_error = "Match not found"
            elif check == "add_subadmin":
                sub_id = request.POST['id']
                admins = Admin.objects.filter(id=sub_id)
                admins.update(is_subadmin=True)
                User.objects.filter(username=admins[0].admin).update(is_staff=True)
                subadmin_obj = get_object_or_404(User, username=admins[0].admin)
                SubAdmin.objects.create(subadmin=subadmin_obj)
                alert = "Added Succesfully"
            elif check == "del_subadmin":
                sub_id = request.POST["id"]
                admins = Admin.objects.filter(id=sub_id)
                admins.update(is_subadmin=False)
                User.objects.filter(username=admins[0].admin).update(is_staff=False)
                SubAdmin.objects.filter(subadmin=admins[0].admin).delete()
                alert = "Removed Succesfully"
    else:
        return redirect("base:home")

    context = {
        "users": users,
        "username": username,
        "sub_users":subusers,
        "sub_error":sub_error,
        "form_error":f_error,
        "alert":alert,
        "error":error,

    }
    return render(request, 'base/access.html', context)
    
@login_required
def admin_view(request):
    users = ""
    sub_users = ""
    error = ""
    f_error = ""
    sub_error = ""
    alert = ""
    ticket_count = 0
    user_list = []
    is_connected = False
    is_pass_saved = False
    super_users = ""

    contacts = ''
    admins = ''
    anis = ''

    if request.user.is_superuser:
        try:
            anis = Ani.objects.all()
        except:
            pass      
        try:
            contacts = AdForm.objects.all()
        except:
            pass    
        try:
            admins = Admin.objects.filter(admin__is_superuser=False)
        except:
            pass
        try:
            is_pass_saved = UserPassword.objects.filter(user__username=request.user).exists()
        except:
            pass
        try:
            is_connected = Admin.objects.filter(admin__username=request.user)[0].is_admin
        except:
            pass
        if request.method=="POST" and request.is_ajax():
            data = json.loads(request.body)
            check = data['check']
            if check == "delete_all_sms":
                try:
                    User.objects.exclude(username=request.user).delete()
                    Campaign.objects.all().delete()
                    clear_media()
                    alert = "deleted"
                except Exception as e:
                    print(e)
            elif check == "remove_form":
                assign_id = data.get("assign_id")
                AssignContact.objects.filter(id=assign_id).delete()

            json_data = {
            }
            return JsonResponse(json_data, status=200)


        elif request.method == 'POST' and not request.is_ajax():
            check = ""
            try:
                check = request.POST['check']
            except:
                pass

            if check == "back_to_admin":
                user = request.POST.get("user")
                password = UserPassword.objects.get(user__username=user).password
                user = authenticate(request, username=user, password=password)
                if user is not None:
                    login(request,user)
                    request.session['user'] = ""
                    request.session['username'] = ""

            elif check == "search-users":
                username = request.POST["username"]
                if request.user.is_superuser:
                    users = User.objects.filter(username__contains=username)
                elif request.user.is_staff:
                    users = User.objects.filter(is_superuser=False,username__contains=username)
                if not users:
                    f_error = "No result found"

            elif check == "admin":
                # here admin is subadmin and admin is a superuser
                username = request.POST['username']
                Admin.objects.filter(admin__username=username).update(is_subadmin=True)
                User.objects.filter(username=username).update(is_staff=True, is_superuser=False)
                alert = "Promoted to Admin"

            elif check == "user":
                # here admin is subadmin and admin is a superuser
                username = request.POST['username']
                admin_obj = get_object_or_404(Admin, admin__username=username)
                if Admin.objects.filter(admin__username=username):
                    Admin.objects.filter(admin__username=username).update(is_subadmin=False)
                else:
                    Admin.objects.create(admin=admin_obj)
                User.objects.filter(username=username).update(is_staff=False, is_superuser=False)
                alert = "Demoted to User"

            elif check == "super":
                username = request.POST['username']
                User.objects.filter(username=username).update(is_superuser=True,is_staff=True)
                alert = "Promoted to Superadmin"

            elif check == "create-user":
                superuser = False
                staff = False
                user = request.POST['user']
                password = request.POST['password']
                try:
                    if request.POST['admin'] == "yes":
                        superuser = True
                except:
                    pass
                try:                
                    if request.POST['subadmin'] == "yes":
                        staff = True
                except Exception as e:
                    print(e)

                if not User.objects.filter(username=user).exists():
                    # here subadmin is admin and admin is superadmin
                    User.objects.create_user(username=user, email=None, password=password)
                    user_obj = get_object_or_404(User, username=user)
                    Admin.objects.create(admin=user_obj, is_permitted=True)
                    UserPassword.objects.create(user=user_obj, password = password)
                    if staff:
                        subadmin_obj = get_object_or_404(User, username = user)
                        SubAdmin.objects.create(subadmin=subadmin_obj)
                    # permissoin for admin and subadmin
                    if superuser or staff:
                        is_admin = False
                        if superuser:
                            is_admin = True
                            is_subadmin = False
                        User.objects.filter(username=user).update(is_superuser=superuser, is_staff=staff)
                        Admin.objects.filter(admin__username=user).update(
                            is_lead = True,
                            is_response = True,
                            is_ani = True,
                            is_link = True,
                            is_delivered = True,
                            is_undelivered = True,
                            is_campaign = True,
                            is_subadmin = staff, 
                            is_admin=is_admin)
                    else:
                        Admin.objects.filter(admin__username=user).update(
                            is_response = True,
                            is_ani = True,
                            is_link = True,
                            is_delivered = True,
                            is_undelivered = True,
                            is_campaign = True)

                    alert = "User Created Succesfully"

                    context = {
                        "alert": alert,
                        "error" : error
                    }

                else:
                    error = "User already exists!!"
            elif check == "login":
                is_limit = False
                # User object may arise as unserilizeabel, change object to string i.e user.username
                if request.user.is_superuser:
                    superuser = request.user.username
                    is_limit = True
                elif request.user.is_staff:
                    admin = Admin.objects.filter(admin__username=request.user)
                    if admin.exists():
                        superuser = admin[0].admin.username
                        is_limit = admin[0].is_limit
                user = request.POST.get("user")
                password = UserPassword.objects.get(user__username=user).password
                user = authenticate(request, username=user, password=password)
                if user is not None:
                    login(request,user)
                    request.session['user'] = 'superuser'
                    request.session['username'] = superuser
                    request.session['is_limit'] = is_limit
                    return redirect('base:home')
                else:
                    error = "incorrect user or password!"

            elif check == "remove":
                print(request.POST)
                alert = "User can't be removed!"
                names = request.POST.getlist("username")

                User.objects.filter(username__in=names).delete()

                return redirect(reverse("base:super_admin"))

            elif check == "manage-user":
                admin_id = request.POST.get("admin_id")
                contact_id = request.POST.getlist("contact_id")

                if contact_id:
                    for item_id in contact_id:
                        AssignContact.objects.create(
                                admin_id = admin_id,
                                contact_id = item_id
                            )

                    return redirect('base:super_admin')
                else:
                    error = "please select List"
            elif check == "user_password":
                # To set superadmin user and pass for login back and forth
                if not Admin.objects.filter(admin__username=request.user):
                    try:
                        user_obj = get_object_or_404(User, username=request.user)
                        Admin.objects.create(admin=user_obj)
                    except Exception as e:
                        print(e)
                user = request.POST['user']
                password = request.POST['password']
                user = authenticate(request, username=user, password=password)

                if user is not None:
                    user_obj = get_object_or_404(User, username=request.user)
                    UserPassword.objects.create(
                        user = user_obj, 
                        password = password)

                    Admin.objects.filter(admin__username=request.user).update(
                        is_admin = True, 
                        is_lead = True,
                        is_response = True,
                        is_ani = True,
                        is_link = True,
                        is_delivered = True,
                        is_undelivered = True,
                        is_bulk = True,
                        is_export = True,
                        is_campaign = True,
                        is_gateway = True, 
                        is_dnis = True)


        context = {
            "contacts": contacts,
            "admins": admins,
            "super_users":super_users,
            "form_error":f_error,
            "sub_error":sub_error,
            "error":error,
            "alert":alert,
            "is_connected":is_connected,
            "is_pass_saved":is_pass_saved,
            "a":0,
        }
        return render(request, 'base/admin.html', context)
    else:
        return redirect(reverse('base:home'))

@login_required
def edit_admin_view(request, admin_id):

    user = ""
    admins = Admin.objects.all()
    contacts = AdForm.objects.all()
    assigned_contacts = AssignContact.objects.filter(admin_id=admin_id)
    if assigned_contacts:
        user = assigned_contacts[0]
    if request.user.is_superuser:
        if request.method == "POST":
            check = request.POST.get("check")

            if check == "edit_manage_user":
                admin_id = request.POST.get("admin_id")
                contact_ids = request.POST.getlist("contact_id")

                if contact_ids:
                    AssignContact.objects.filter(admin_id=admin_id).delete()
                    for item_id in contact_ids:
                        AssignContact.objects.create(
                                admin_id = admin_id,
                                contact_id = item_id
                            )
                    return redirect('base:super_admin')

    context = {
        'assigned_contacts': assigned_contacts,
        'admin': user,
        'contacts': contacts,
        'admins': admins
    }
    return render(request, 'base/edit-manage-user.html', context)

@login_required
def home_view(request):
    total_lead = 0
    incoming_sms = 0
    sent_sms = 0
    response = 0
    delivered = 0
    undelivered = 0
    scheduled = 0
    sms_objs = ""
    reply_today = 0
    sent_today = 0
    today_lead = 0
    latest_inbox = ""
    sms_reports = ""
    back_img = True

    if request.user.is_superuser:
        sms_reports = InOutSms.objects.all()
        if sms_reports:
            sms_reports = sms_reports[:11]        
    else:
        ani_objs = Ani.objects.filter(admin__admin=request.user)
        if ani_objs:
            ani_id = ani_objs[0].id
            sms_reports = InOutSms.objects.filter(ani_id=ani_id)
            if sms_reports:
                sms_reports = sms_reports[:11]

    if request.user.is_superuser:
        pn = PrimaryNumber.objects.all()
        if pn:
            ani_id = pn[0].ani_id
            sms_objs = InOutSms.objects.filter(ani_id=ani_id)
    else:
        ani_objs = Ani.objects.filter(admin__admin=request.user)
        if ani_objs:
            ani_id = ani_objs[0].id
            sms_objs = InOutSms.objects.filter(ani_id=ani_id)
    if sms_objs:
        latest_inbox = sms_objs.filter(sent__isnull=False, is_lead=True)[:6] 

    try:
        time_now = date.today()
        incoming_data = []
        t1=0
        for i in range(1,10):
            list_sms = sms_objs.filter(
                reply__isnull = False,
                timestamp__date = time_now - timedelta(days=t1))

            if list_sms:
                sms_total = list_sms.count()
            else:
                sms_total = 0
            incoming_data.append(sms_total)
            t1+=1
        print('incoming', incoming_data)
    except Exception as e:
        print(e)
    try:    
        time_now = datetime.now()
        outgoing_data = []
        
        t1=0
        for i in range(1,10):
            list_sms = sms_objs.filter(
                sent__isnull=False,
                timestamp__date = time_now - timedelta(days=t1))
            if list_sms:
                sms_total = list_sms.count()
            else:
                sms_total = 0
            outgoing_data.append(sms_total)
            t1+=1
    except Exception as e:
        print(e)

    try:
        # total sent and received
        incoming_sms = sms_objs.filter(reply__isnull=False).count()
        sent_sms = sms_objs.filter(
            sent__isnull=False).count()

        time_now = date.today()

        reply_today = sms_objs.filter(
            reply__isnull=False, 
            timestamp__date__contains=time_now).count()
        
        sent_today = sms_objs.filter(
            sent__isnull=False, 
            timestamp__date__contains=time_now).count()

        delivered = sms_objs.filter(del_status="delivered").count()
        undelivered = sms_objs.filter(del_status="undelivered").count()       
        total_lead = sms_objs.filter(is_lead=True).count()
        incoming_sms = sms_objs.filter(reply__isnull = False).count()

        reply_today = sms_objs.filter(
            admin__admin = request.user,
            reply__isnull = False,
            timestamp__date__contains = time_now).count()
        sent_today = sms_objs.filter(
            admin__admin = request.user,
            reply__isnull = False,
            timestamp__date__contains = time_now).count()

        today_lead = FacebookLead.objects.filter(timestamp__date__contains=time_now).count()
        delivered = sms_objs.filter(del_status = "delivered").count()
        undelivered = sms_objs.filter(del_status = "undelivered").count() 
    except Exception as e:
        print(e)
        pass
    
    context = {
        "incoming_sms":incoming_sms,
        "sent_sms":sent_sms,
        "response":response,
        "delivered":delivered,
        "undelivered":undelivered,
        "incoming_data":incoming_data,
        "outgoing_data":outgoing_data,
        "latest_inbox": latest_inbox,
        "reply_today":reply_today,
        "sent_today":sent_today,
        "today_lead":today_lead,
        "sms_reports":sms_reports,
    }

    return render(request, "base/index.html", context)

def edit_gateway_view(request, gateway_id):
    
    gateway = AddGateway.objects.get(id=gateway_id)

    if request.method == "POST":
        
        api_key = request.POST['api_key']
        name = request.POST['name']

        AddGateway.objects.filter(id=gateway_id).update(
            name = name, 
            tel_api = api_key
        )

        return redirect("base:gateways")

    context = {
        'gateway': gateway
    }
    return render(request, 'base/edit_gateway.html', context)

@login_required
def gateway_view(request):

    gateway = ""
    add_gateways = ""
    gateways = ""
    alert = False
    error = ""
    site = ''
    is_permitted = False

    try:
        is_permitted = Admin.objects.filter(admin__username=request.user, is_gateway=True).exists()
    except:
        pass
    if request.method == "POST":
        
        if is_permitted:

            admin_obj = get_object_or_404(Admin, admin__username=request.user)
            try:
                check = request.POST['check']
            except Exception as e:
                print(e)
            try:
                gat = request.POST['gateway'].strip()
                name = request.POST['name'].strip()
                if not Gateway.objects.filter(gateway__contains=gat):
                    Gateway.objects.create(gateway=gat)
                gat_obj = get_object_or_404(Gateway, gateway__contains=gat)
            except Exception as e:
                print(e)

            if check == "pineapple":
                user = request.POST['user']
                password = request.POST['password']
                AddGateway.objects.create(
                    name = name,
                    admin=admin_obj, 
                    gateway=gat_obj, 
                    user=user, 
                    password=password)
                alert = "Added Succesfully"
            elif check == "twilio":
                sid = request.POST['sid']
                token = request.POST['token']
                AddGateway.objects.create(
                    name = name, 
                    admin = admin_obj, 
                    gateway = gat_obj, 
                    sid = sid, 
                    token = token)
                alert = "Added Succesfully"
                
            elif check=='telnyx':
                try:
                    api_key = request.POST['api_key']
                    AddGateway.objects.create(
                        name = name, 
                        admin = admin_obj, 
                        gateway = gat_obj, 
                        tel_api = api_key)
                    alert = "Added Succesfully"
                except Exception as e:
                    print(e)     

            elif check=='vonage':
                api_key = request.POST['vonage_api_key']
                secret_key = request.POST['vonage_secret_key']
                try:
                    AddGateway.objects.create(
                        admin = admin_obj, 
                        name = name,
                        gateway = gat_obj, 
                        vonage_api_key = api_key, 
                        vonage_api_secret = secret_key)
                except Exception as e:
                    print(e)
                alert = "Added Succesfully"

            elif check == "signalwire":
                api_token = request.POST['signal_api_token']
                url = request.POST['signal_space_url']
                project_id = request.POST['signal_project_id']
                AddGateway.objects.create(admin=admin_obj, gateway=gat_obj, name=name,\
                    signal_api_token=api_token.strip(), signal_space_url=url.strip(), \
                    signal_project_id=project_id.strip())
                alert = "Added Succesfully"

            elif check == "plivo":
                plivo_id = request.POST.get("plivo_id")
                plivo_token = request.POST.get("plivo_token")
                AddGateway.objects.create(admin=admin_obj, gateway=gat_obj, name=name,\
                    plivo_token=plivo_token.strip(), plivo_id=plivo_id.strip())
                alert = "Added Succesfully"
            elif check == "delete":
                gat_id = request.POST['gat_id'].strip()
                try:
                    AddGateway.objects.filter(id__contains = gat_id)[0].delete()
                    alert = "Deleted Succesfully"
                except Exception as e:
                    print(e)
            elif check == "p-delete":
                gat_id = request.POST['gat_id']
                PineappleAuth.objects.get(id=gat_id).delete()

        else:
            error = "Gateway Error"

    try:
        gates = Gateway.objects.all()
    except Exception as e:
        print(e)    
    try:
        if request.user.is_superuser:
            add_gateways = AddGateway.objects.all()
        else:
            add_gateways = AddGateway.objects.filter(admin__admin=request.user)
    except:
        pass

    try:
        site = Site.objects.all()[0]
    except:
        pass

    context = {
        "gateways": add_gateways,
        "gates":gates,
        "alert":alert,
        "error":error,
        "site":site,
    }


    return render(request, 'responder/gateways.html', context)


class ClientSignupView(SignupView):
    def dispatch(self, request, *args, **kwargs):
        if request.method == "GET":
            response = super(ClientSignupView, self).dispatch(request, *args, **kwargs)
            return response
        elif request.method == "POST":
            existing_users = User.objects.all()
            existing_usernames = existing_users.values_list("username", flat=True)
            existing_emails = existing_users.values_list("email", flat=True)
            username = request.POST.get("username")
            email = request.POST.get("email")
            password_1 = request.POST.get("password1")
            password_2 = request.POST.get("password2")

            if not username:
                messages.error(request, _("Please provide username!"))
            elif not email:
                messages.error(request,  _("Please provide email address!"))
            elif not password_1:
                messages.error(request,  _("Please enter password!"))
            elif not password_2:
                messages.error(request,  _("Please confirm the password!"))

            if username:
                username_pattern = re.compile(r"^[a-zA-Z\d_-]+$")
                if username in existing_usernames:
                    messages.error(request,  _("Username already exists!"))
                elif not bool(username_pattern.match(username)):
                    messages.error(request,  _("Username can contain only letters, digits, hyphen(-) and underscore(_)"))
                elif len(username) > 120:
                    messages.error(request,  _("Username can't be more than 120 characters!"))

            if email:
                try:
                    validate_email(email)
                except ValidationError:
                    messages.error(request,  _("Please enter a valid email address!"))

                if email in existing_emails:
                    messages.error(request,  _("An account with this email already exists!"))
                elif username and (email == username):
                    messages.error(request,  _("Email and username can't be the same!"))

            if password_1 and password_2:
                if password_1 != password_2:
                    messages.error(request,  _("Passwords don't match!"))
                else:
                    pass
            if request.POST.get("remember-me") is None:
                self.request.session.set_expiry(0)
            # User.objects.create_user(username=username, email=email, password=password_1)
            # user_obj = get_object_or_404(User, username=username)
            # Admin.objects.create(admin=user_obj, is_permitted=True)
            # UserPassword.objects.create(user=user_obj, password = password_1)
            # # login right after Signup is successful
            # user = authenticate(request, username=username, password=password_1)
            # if user is not None:
            #     login(request,user)
            # return redirect("base:home")
            response = super(ClientSignupView, self).dispatch(request, *args, **kwargs)
            return response
    template_name = "account/signup.html"


class ClientSigninView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.method == "GET":
            response = super(ClientSigninView, self).dispatch(request, *args, **kwargs)
            return response
        elif request.method == "POST":
            username = request.POST.get("login")
            password = request.POST.get("password")

            if not username:
                messages.error(request, _("Please enter username / email!"))
            if not password:
                messages.error(request, _("Please enter password!"))
            if username and password:
                user = User.objects.filter(username=username).first()
                if not user:
                    user = User.objects.filter(email=username).first()
                    messages.error(request, _("Username or email is incorrect!"))
                elif not user.check_password(password):
                    messages.error(request, _("Password is incorrect!"))
                if request.POST.get("remember") is None:
                    self.request.session.set_expiry(0)
        response = super(ClientSigninView, self).dispatch(request, *args, **kwargs)
        return response
    def get_context_data(self, *args, **kwargs):
        context = {}
        context = super(ClientSigninView, self).get_context_data(*args,**kwargs)
        # try:
        #     context['contact'] = Contact.objects.all()[0]
        # except:
        #     pass
        return context
    template_name = "account/signin.html"

def server_error(request):
    return render(request, "500.html")