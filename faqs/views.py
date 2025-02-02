import yaml

from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.views import View
from faqs.lib import create_new_faq_entry, delete_faq, maybe_get_faq_data


class FAQ(View):
    def get(self, request):
        # If no language is provided, default it
        # to English ("en")
        lang = request.GET.get("lang", "en")

        faq_data = maybe_get_faq_data(lang)

        if faq_data is None:
            return JsonResponse({"error": "Language not supported!"}, status=400)

        response_data = {
            "faqs": faq_data,
        }

        return JsonResponse(response_data)

    def delete(self, request):
        id = request.GET.get("id")

        if id is None:
            return JsonResponse({"error": "FAQ ID not mentioned"}, status=400)

        try:
            faq_id = int(id)
        except ValueError:
            return JsonResponse(
                {"error": "ID parameter must be an integer."}, status=400
            )

        delete_faq(faq_id)

        return JsonResponse({"success": "Successfully deleted FAQ entry!"})

    def post(self, request):
        question = request.GET.get("question")
        answer = request.GET.get("answer")

        if question is None or answer is None:
            return JsonResponse({"error": "Missing FAQ question or answer!"}, status=400)

        async_to_sync(create_new_faq_entry)(question, answer)

        return JsonResponse({"success": "Successfully created new FAQ entry!"})


class SchemaView(View):
    def get(self, request):
        with open("faqs/faqs.yaml", "r") as stream:
            try:
                schema = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                return JsonResponse(
                    {"error": "Failed to load OpenAPI schema"}, status=500
                )
        return JsonResponse(schema, safe=False)
