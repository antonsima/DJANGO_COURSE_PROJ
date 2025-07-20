from allauth.account.views import SignupView


class CustomSignupView(SignupView):
    template_name = "account/signup.html"
