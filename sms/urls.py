from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from rest_framework import routers

from sms.views import SMSView

# router = routers.DefaultRouter()
#
# router.register(r'inbound/sms$', SMSView.inbound)

urlpatterns = [
    url(r'inbound/sms$', SMSView.inbound),
    url(r'outbound/sms$', SMSView.outbound),
]

urlpatterns = format_suffix_patterns(urlpatterns)
