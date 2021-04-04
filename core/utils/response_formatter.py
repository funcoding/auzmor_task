from rest_framework.response import Response


class ResponseFormatterUtil:
    @staticmethod
    def success(data, response_code=200):
        return Response({"message": data, "error": None}, status=response_code)

    @staticmethod
    def error(message, response_code=500):
        return Response({"message": None, "error": message}, status=response_code)

    @staticmethod
    def form_validation_error(data):
        return Response({"message": "", "error": data.values()}, status=422)
