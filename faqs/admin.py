from asgiref.sync import async_to_sync
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from faqs.models import FAQ, FAQTranslation, Language
from faqs.lib import create_new_faq_entry, delete_faq


# Custom filter to filter FAQs by translation language
class LanguageFilter(SimpleListFilter):
    title = "Language"
    parameter_name = "lang"

    def lookups(self, request, model_admin):
        # Define the available languages in the filter dropdown
        return [(lang_code, lang) for lang_code, lang in Language.choices]

    def queryset(self, request, queryset):
        # If a language is selected in the filter, filter FAQs based on it
        if self.value():
            lang_code = self.value()

            return queryset.filter(lang=lang_code)

        return queryset.filter(lang=Language.EN)


class FAQAdmin(admin.ModelAdmin):
    list_display = ("faq_id", "lang", "question", "answer")
    fields = ("question", "answer")
    list_filter = (LanguageFilter,)
    search_fields = ("question", "answer")

    # We override the save method to create instances
    # of translations of the FAQ as well.
    def save_model(self, request, obj, form, change):
        async_to_sync(create_new_faq_entry)(obj.question, obj.answer)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            delete_faq(obj.faq_id)

    def delete_model(self, request, obj):
        delete_faq(obj.faq_id)


# Register the model with the admin panel
admin.site.register(FAQTranslation, FAQAdmin)
