from django.shortcuts import render, redirect
import random
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.functions import Now
from datetime import timedelta
from django.db.models import Q
from django.contrib import messages
from .models import Account, Action

# Create your views here.

def generate_unique_account_number():
        not_unique = True
        while not_unique:
            unique_ref = random.randint(1000000000, 9999999999)
            if not Account.objects.filter(account_number=unique_ref):
                not_unique = False

        return int(unique_ref)

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        password = request.POST.get('password1')
        if form.is_valid:
            if len(password) <= 8:
                messages.error(request, 'password should have minimum 8 characters')
            elif password.isalpha():
                messages.error(request, 'password must contain at least a number')
            elif ' ' in password:
                messages.error(request, "password shouldn't contain spaces")
            elif password.isdigit():
                messages.error(request, 'passoword must contain letters')
            else:
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()

                login(request, user)

                Account.objects.create(
                    user=request.user,
                    balance=1000.00,
                    account_number=generate_unique_account_number(),
                    account_name=request.user.username
                )

                return redirect('home')


    context = {'form': form}
    return render(request, 'base/register.html', context)

@login_required(login_url='/login')
def logoutUser(request):
    logout(request)
    return redirect('login')

def loginUser(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            User.objects.get(username=username)
        except:
            messages.error(request, 'user not found')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'username or password is not correct')

    return render(request, 'base/login.html')

@login_required(login_url='/login')
def home(request):
    actions = Action.objects.all()
    account = Account.objects.get(user=request.user)

    filtered_actions = []

    for action in actions:
        if action.receiver_account == account or action.account == account:
            filtered_actions.append(action)

    context = {'account': account, 'actions': filtered_actions[:3]}
    return render(request, 'base/home.html', context)


@login_required(login_url='/login')
def transferPage(request, pk):
    senders_account = Account.objects.get(id=pk)

    if request.method == 'POST':
        amount_to_send = request.POST.get('amount')
        receiver_account_number = request.POST.get('receiverAccountNumber')

        receiver_account = Account.objects.get(account_number=receiver_account_number)

        action = Action.objects.create(
            account=senders_account,
            receiver_account=receiver_account,
            amount=amount_to_send,
            transaction_type='transfer'
        )

        return redirect('confirm-transfer', action.id)

    context = {'account': senders_account}
    return render(request, 'base/transferpage.html', context)

@login_required(login_url='/login')
def confirmTransferPage(request, pk):
    action = Action.objects.get(id=pk)
    senders_account = action.account
    receivers_account = action.receiver_account
    amount = action.amount

    if request.method == 'POST':
        password = request.POST.get('password')

        authenticate_user = authenticate(request, username=request.user.username, password=password)
        if authenticate_user is not None:
            senders_account.balance = senders_account.balance - amount
            receivers_account.balance = receivers_account.balance + amount
            senders_account.save(update_fields=["balance"])
            receivers_account.save(update_fields=["balance"])

            messages.success(request, 'transferred successfully')

            return redirect('home')
        else:
            messages.error(request, 'incorrect password')

    context = {'account': senders_account, 'action': action}
    return render(request, 'base/confirm_transfer.html', context)

@login_required(login_url='/login')
def go_back(request, pk):
    action = Action.objects.get(id=pk)
    action.delete()
    return redirect('home')

@login_required(login_url='/login')
def addPage(request):
    account = Account.objects.get(user=request.user)

    context = {'account': account}
    return render(request, 'base/add_page.html', context)

@login_required(login_url='/login')
def historyPage(request):
    account = Account.objects.get(user=request.user)
    q = ''

    if request.GET.get('q') is not None:
        q = request.GET.get('q')

    if 'lastweek' in q:
        current_day =  datetime.datetime.today().day
        current_month = datetime.datetime.today().month
        current_year = datetime.datetime.today().year

        end_filter_date = f'{current_year}-{current_month}-{current_day-7}'
        start_filter_date = f'{current_year}-{current_month}-{current_day-14}'

        print(start_filter_date)
        print(end_filter_date)

        actions = Action.objects.filter(created__range=[start_filter_date, end_filter_date])
    elif 'lastmonth' in q:
        current_day =  datetime.datetime.today().day
        current_month = datetime.datetime.today().month
        current_year = datetime.datetime.today().year

        end_filter_date = f'{current_year}-{current_month-1}-{current_day}'
        start_filter_date = f'{current_year}-{current_month-2}-{current_day}'

        actions = Action.objects.filter(created__range=[start_filter_date, end_filter_date])
    elif 'lastyear' in q:
        current_day =  datetime.datetime.today().day
        current_month = datetime.datetime.today().month
        current_year = datetime.datetime.today().year

        end_filter_date = f'{current_year-1}-{current_month}-{current_day}'
        start_filter_date = f'{current_year-2}-{current_month}-{current_day}'

        actions = Action.objects.filter(created__range=[start_filter_date, end_filter_date])
    elif request.method == 'POST':
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')

        actions = Action.objects.filter(created__range=[startdate, enddate])
    else:
        actions = Action.objects.all()


    filtered_actions = []

    for action in actions:
        if action.account == account or action.receiver_account == account:
            if q != '' and q != 'lastweek' and q != 'lastmonth':
                if q in str(action.amount) or q in str(action.receiver_account.account_name):
                    filtered_actions.append(action)
            else:
                filtered_actions.append(action)

    context = {'account': account, 'actions': filtered_actions, 'past_day': datetime.date.today().day-2,'current_day': datetime.date.today().day, 'current_month': datetime.date.today().month, 'current_year': datetime.date.today().year}
    return render(request, 'base/history_page.html', context)

@login_required(login_url='/login')
def changePassword(request):
    account = Account.objects.get(user=request.user)
    actions = Action.objects.all()

    filtered_actions = []

    for action in actions:
        if action.receiver_account == account or action.account == account:
            filtered_actions.append(action)

    if request.method == 'POST':
        old_password = request.POST.get('old-password')
        new_password = request.POST.get('new-password')
        confirm_new_password = request.POST.get('confirm-new-password')

        user = authenticate(username=request.user.username, password=old_password)
        if user is not None:
            if new_password == confirm_new_password:
                if len(new_password) <= 8:
                    messages.error(request, 'password should have minimum 8 characters')
                elif new_password.isalpha():
                    messages.error(request, 'password must contain at least a number')
                elif new_password.isdigit():
                    messages.error(request, 'passoword must contain letters')
                else:
                    user_ = User.objects.get(username=request.user.username)
                    user_.set_password(new_password)
                    user_.save()

                    messages.success(request, 'password changed successfully')
                    return redirect('home')
            else:
                messages.error(request, "passwords don't match")
        else:
            messages.error(request, 'password is incorrect')

    context = {'account': account, 'actions': filtered_actions[:3]}
    return render(request, 'base/change_password.html', context)

@login_required(login_url='/login')
def editAccount(request):
    account = Account.objects.get(user=request.user)

    if request.method == 'POST':
        new_username = request.POST.get('account_name_')
        user = User.objects.get(username=request.user.username)
        account = Account.objects.get(user=user)

        user.username = new_username
        user.save(update_fields=["username"])

        account.account_name = new_username
        account.save(update_fields=["account_name"])

        messages.success(request, 'username changed successfully')

        return redirect('home')

    context = {'account': account}
    return render(request, 'base/edit_account.html', context)