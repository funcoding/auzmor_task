from rest_framework import serializers


def construct_error_messages(param_name=''):
    return {
        'required': f'{param_name} is missing',
        'min_length': f'{param_name} is invalid',
        'max_length': f'{param_name} is invalid'
    }


class SmsSerializer(serializers.Serializer):
    from_number = serializers.CharField(
        min_length=6,
        max_length=16,
        error_messages=construct_error_messages('from')
    )
    to_number = serializers.CharField(
        min_length=6,
        max_length=16,
        error_messages=construct_error_messages('to')
    )
    text = serializers.CharField(
        min_length=1,
        max_length=120,
        error_messages=construct_error_messages('text')
    )
