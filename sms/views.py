from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.core.cache import cache

from core.exceptions.custom_handler import ApiError
from core.utils.response_formatter import ResponseFormatterUtil
from phone_number.models import PhoneNumber
from sms.validators.sms_validator import InboundSmsSerializer


class SMSView(APIView):
    renderer_classes = [JSONRenderer]

    @staticmethod
    @api_view(http_method_names=['POST'])
    def inbound(request):
        serialized_data = InboundSmsSerializer(
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
                f"{request.META['user'].id}_{serialized_data.validated_data['from_number']}",
                [serialized_data.validated_data['to_number']],
                86400
            )

        return ResponseFormatterUtil.success("inbound sms ok")

    @staticmethod
    @api_view(http_method_names=['POST'])
    def outbound(request):
        serialized_data = InboundSmsSerializer(
            data={**request.data, 'from_number': request.data.get('from'), 'to_number': request.data.get('to')}
        )
        serialized_data.is_valid(raise_exception=True)
        record_count = PhoneNumber.objects.filter(
            account_id=request.META['user'].id,
            number=serialized_data.validated_data['from_number']
        ).count()

        if record_count == 0:
            raise ApiError(message='from parameter not found')
        cached_record = cache.get(f"{request.META['user'].id}_{serialized_data.validated_data['from_number']}")

        if cached_record is None:
            raise ApiError("No cache present")

        if len(cached_record) == 1:
            raise ApiError(f"limit reached for {serialized_data.validated_data['from_number']}")

        if serialized_data.validated_data['to_number'] in cached_record:
            raise ApiError(
                f"sms from {serialized_data.validated_data['from_number']} to {serialized_data.validated_data['to_number']} blocked by STOP request")

        return ResponseFormatterUtil.success("outbound sms ok")

