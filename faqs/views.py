from django.http import JsonResponse
from django.views import View
from faqs.lib import maybe_get_faq_data


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

