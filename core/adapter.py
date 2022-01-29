from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpResponseRedirect
from rest_framework_simplejwt.tokens import RefreshToken

class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):

        url = request.session["next_URL"]
        refresh = RefreshToken.for_user(request.user)
        str1 = "?access_token=" + str(refresh.access_token)
        str2 = "&refresh_token=" + str(refresh)

        return (url + str1 + str2)


# http://127.0.0.1:8000/accounts/login/?next=https://restaurant.urbantandoor.in/
# https://api.urbantandoor.in/accounts/login/?next=https://restaurant.urbantandoor.in/