import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes, force_str
from django.views import View
from django.conf import settings
from .tokens import TokenGenerator, generate_token
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator

User = get_user_model()

# Activate Account View
class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            # Decode the UID and get the user
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            user = None
        
        # Check if the user exists and the token is valid
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True  # Activate the user
            user.save()
            messages.info(request, "Account activated successfully!")
            return redirect('/authentication/login')
        else:
            messages.error(request, "Activation link is invalid or has expired.")
            return render(request, 'authentication/activate_failed.html')

# Password Reset
class RequestResetEmailView(View):
    def get(self, request):
        return render(request, 'request_reset_email.html')

    def post(self, request):
        email = request.POST['email']
        user = User.objects.filter(email=email)
        if user.exists():
            current_site = get_current_site(request)
            email_subject = '[Reset Your Password]'
            message = render_to_string('reset_user_password.html', {
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0])
            })
            email_message = EmailMessage(email_subject, message, 'your-email@example.com', [email])
            email_message.send()
            messages.info(request, "We have sent you an email with instructions on how to reset the password.")
        else:
            messages.error(request, "No user found with that email address.")
        return render(request, 'request_reset_email.html')


class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))  # Correct variable name here
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.warning(request, "Password reset link is invalid or has expired.")
                return render(request, 'request_reset_email.html')
        except DjangoUnicodeDecodeError:
            pass  # Handle invalid UID decoding gracefully
        return render(request, 'set_new_password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']
        if password != confirm_password:
            messages.warning(request, "Passwords do not match.")
            return render(request, 'set_new_password.html', context)
        else:
            try:
                user_id = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=user_id)
                if PasswordResetTokenGenerator().check_token(user, token):
                    user.set_password(password)
                    user.save()
                    messages.success(request, "Password has been successfully reset. You can now log in.")
                    return redirect('login')  # Redirect to the login page
                else:
                    messages.warning(request, "The password reset link is invalid or expired.")
            except DjangoUnicodeDecodeError:
                messages.error(request, "Something went wrong while resetting your password.")
        return render(request, 'set_new_password.html', context)

    

# SignUp View
@csrf_protect
def signup(request):
    print("Request Method:", request.method)

    if request.method == "GET":
        return render(request, "authentication/signup.html")

    if request.method == "POST":
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST  # Handle both JSON and form data
            
            print("Received Data:", data)

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            # Validate email
            try:
                EmailValidator()(email)
            except ValidationError:
                return JsonResponse({"success": False, "message": "Invalid email format"})

            # Check if passwords match
            if password != confirm_password:
                return JsonResponse({"success": False, "message": "Passwords do not match"})

            # Debugging: Check if email exists
            existing_user = User.objects.filter(email=email)
            print(f"Existing users with email {email}: {existing_user}")

            if existing_user.exists():
                print("Email is already taken.")
                return JsonResponse({"success": False, "message": "Email is already taken"})

            # Create the user
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = name
            user.is_active = False  # Account inactive until activation
            user.is_staff = False
            user.save()

            print(f"User {email} created successfully!")

            return JsonResponse({"success": True, "message": "Account created successfully. Please check your email to activate your account."})

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"success": False, "message": f"Error creating account: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method."})


## Login
@ensure_csrf_cookie
def login(request):
    if request.method == "GET":
        # Render the login page if the request is a GET request
        return render(request, "authentication/login.html")

    if request.method == "POST":
        try:
            # ✅ Parse JSON request body to extract login details
            data = json.loads(request.body.decode("utf-8"))

            username = data.get('email', '').strip()
            password = data.get('password', '').strip()

            # ✅ Check if email and password fields are provided
            if not username or not password:
                return JsonResponse({
                    "success": False,
                    "message": "Email and password are required."
                }, status=400)

            try:
                # ✅ Check if the user exists in the database
                user = User.objects.get(email=username)

                # ✅ If user exists but is inactive, deny login
                if not user.is_active:
                    return JsonResponse({
                        "success": False,
                        "message": "Account is inactive. Please activate your account."
                    }, status=400)

            except User.DoesNotExist:
                # ✅ If the user does not exist, return an error
                return JsonResponse({
                    "success": False,
                    "message": "Invalid Credentials"
                }, status=400)

            # ✅ Authenticate the user (check if password is correct)
            myuser = authenticate(request, username=username, password=password)

            if myuser is not None:
                # ✅ If authentication is successful, log the user in
                auth_login(request, myuser)

                # ✅ Redirect users based on their role:
                # If the user is both staff and superuser, redirect to admin dashboard
                # Otherwise, redirect to the profile page
                if myuser.is_staff and myuser.is_superuser:
                    redirect_url = "/admin-panel/admin-dashboard/"
                else:
                    redirect_url = "/profile"

                # ✅ Send success response with appropriate redirect URL
                return JsonResponse({
                    "success": True,
                    "message": "Login Successful",
                    "redirect_url": redirect_url
                }, status=200)

            else:
                # ✅ If authentication fails (wrong password), return an error
                return JsonResponse({
                    "success": False,
                    "message": "Invalid Credentials"
                }, status=400)

        except json.JSONDecodeError:
            # ✅ If the request body is not valid JSON, return an error
            return JsonResponse({
                "success": False,
                "message": "Invalid request format"
            }, status=400)

    # ✅ If the request method is not POST or GET, return an error
    return JsonResponse({
        "success": False,
        "message": "Invalid request method"
    }, status=405)


## Logout
def logout_view(request):
    logout(request)
    messages.info(request, "Logout Success")
    return redirect('/auth/login/')