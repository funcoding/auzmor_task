from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.core.cache import cache

from core.exceptions.custom_handler import ApiError
from core.utils.response_formatter import ResponseFormatterUtil
from phone_number.models import PhoneNumber
from sms.validators.sms_validator import SmsSerializer


class SMSView(APIView):
    renderer_classes = [JSONRenderer]
    SECONDS_IN_4_HOURS = 14400
    SECONDS_IN_24_HOURS = 86400

    @staticmethod
    @api_view(http_method_names=['POST'])
    def inbound(request):
        serialized_data = SmsSerializer(
            data={**request.data, 'from_number': request.data.get('from'), 'to_number': request.data.get('to')}
        )
        serialized_data.is_valid(raise_exception=True)
        record_count = PhoneNumber.objects.filter(
            account_id=request.META['user'].id,
            number=serialized_data.validated_data['to_number']
        ).count()

        if record_count == 0:
            raise ApiError(message='to parameter not found')

        if serialized_data.validated_data['text'].strip() == 'STOP':
            cache.set(
                f"inbound:account_id:{request.META['user'].id}:{serialized_data.validated_data['from_number']}:{serialized_data.validated_data['to_number']}",
                "",
                SMSView.SECONDS_IN_4_HOURS
            )

        return ResponseFormatterUtil.success("inbound sms ok")

    @staticmethod
    @api_view(http_method_names=['POST'])
    def outbound(request):
        serialized_data = SmsSerializer(
            data={**request.data, 'from_number': request.data.get('from'), 'to_number': request.data.get('to')}
        )
        serialized_data.is_valid(raise_exception=True)

        throttled_record = cache.get_or_set(
            f"throttle:account_{request.META['user'].id}:number_{serialized_data.validated_data['from_number']}", 1,
            SMSView.SECONDS_IN_24_HOURS)

        if throttled_record == 50:
            raise ApiError(f"limit reached for from {serialized_data.validated_data['from_number']}")

        cached_inbound_record = cache.get(f"inbound:account_id:{request.META['user'].id}:{serialized_data.validated_data['from_number']}:{serialized_data.validated_data['to_number']}")

        if cached_inbound_record is not None:
            raise ApiError(
                f"sms from {serialized_data.validated_data['from_number']} to {serialized_data.validated_data['to_number']} blocked by STOP request"
            )

        cache.incr(f"throttle:account_{request.META['user'].id}:number_{serialized_data.validated_data['from_number']}")

        record_count = PhoneNumber.objects.filter(
            account_id=request.META['user'].id,
            number=serialized_data.validated_data['from_number']
        ).count()

        if record_count == 0:
            raise ApiError(message='from parameter not found')

        return ResponseFormatterUtil.success("outbound sms ok")

