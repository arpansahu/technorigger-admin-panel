import ssl

from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, RedirectView
from django.utils.translation import gettext_lazy as _

from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm, PasswordResetForm, LoginForm
from django.conf import settings
from django.contrib.auth.views import PasswordContextMixin

from account.models import Account
from account.token import account_activation_token

DOMAIN = settings.DOMAIN
PROTOCOL = settings.PROTOCOL

from mailjet_rest import Client

mailjet = Client(auth=(settings.MAIL_JET_API_KEY, settings.MAIL_JET_API_SECRET), version='v3.1')


# Create your views here.

class CustomPasswordResetView(PasswordContextMixin, FormView):
    email_template_name = "registration/password_reset_email.html"
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")
    template_name = "registration/password_reset_form.html"
    title = _("Password reset")
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)


def send_mail_account_activate(reciever_email, user, SUBJECT="Confirm Your Email"):
    message = render_to_string(template_name='account/activate_account_mail.html', context={
        'user': user,
        'protocol': PROTOCOL,
        'domain': DOMAIN,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })

    data = {
        'Messages': [
            {
                "From": {
                    "Email": settings.MAIL_JET_EMAIL_ADDRESS,
                    "Name": "Borcelle CRM"
                },
                "To": [
                    {
                        "Email": reciever_email,
                        "Name": "Dear User"
                    }
                ],
                "Subject": SUBJECT,
                "TextPart": message,
                "HTMLPart": f"<h3>Dear {user.username}, Message: {message}",
                "CustomID": f"{reciever_email}"
            }
        ]
    }
    result = mailjet.send.create(data=data)
    print("account activation mail send")
    return result


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'account/account_activation_done.html', context={'message': 'Thank you for your email '
                                                                                           'confirmation. Now you can '
                                                                                           'login your account.'})
    else:
        return render(request, 'account/account_activation_done.html', context={'message': 'Activation link is invalid!'})


class RegistrationView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        form = RegistrationForm()
        context['registration_form'] = form
        return render(request, 'account/register.html', context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = RegistrationForm(request.POST)
        if form.is_valid():
            account = form.save()
            email = form.cleaned_data.get('email')
            send_mail_account_activate(email, account)
            return render(request, 'account/account_activation_done.html', {'message': 'Check your mail and activate your account'})
        else:
            context['registration_form'] = form
        return render(request, 'account/register.html', context)


@method_decorator(login_required(redirect_field_name=''), name='dispatch')
class LogoutView(RedirectView):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')


class LoginView(View):
    def get(self, request):
        form = LoginForm(request.POST or None)
        msg = None
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, "account/login.html", {"form": form, "msg": msg})

    def post(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(email=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

        return render(request, "account/login.html", {"form": form, "msg": msg})


@method_decorator(login_required(redirect_field_name=''), name='dispatch')
class AccountView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        form = AccountUpdateForm(
            initial={
                "email": request.user.email,
                "username": request.user.username,
            }
        )
        context['account_form'] = form
        return render(request, 'account/account.html', context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()

        context['account_form'] = form
        return render(request, 'account/account.html', context)
