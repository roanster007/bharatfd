from googletrans import Translator

from asgiref.sync import sync_to_async
from django.db import transaction
from django.http import JsonResponse
from faqs.models import FAQ, FAQTranslation, Language

translator = Translator()
supported_langs = [lang.value for lang in Language]


# For each FAQ, we create a new row in the FAQ table
# which stores the query as it receives with no translation.
# This serves as the main reference point to the FAQ.
async def create_new_faq_entry(question, answer):
    base_lang = await translator.detect(answer)

    if base_lang.lang not in supported_langs:
        return JsonResponse({"error": "Language not supported!"}, status=400)

    faq, created = await sync_to_async(
        FAQ.objects.get_or_create, thread_sensitive=True
    )(base_lang=base_lang.lang, question=question, answer=answer)

    if created:
        await create_translations(faq, question, answer)


# Once we create a main FAQ reference, we want to create
# all the Translation instances in all the supported languages
# for the FAQ question and answer, and store it in the
# FAQTranslations table, which references to the main
# FAQ entry in FAQ table via ForeignKey.
async def create_translations(faq, question, answer):
    translations = []

    for lang in supported_langs:
        translated_question = await translator.translate(question, dest=lang)
        translated_answer = await translator.translate(answer, dest=lang)

        faq_translation = FAQTranslation(
            faq=faq,
            lang=lang,
            question=translated_question.text,
            answer=translated_answer.text,
        )

        translations.append(faq_translation)

    await sync_to_async(FAQTranslation.objects.bulk_create, thread_sensitive=True)(
        translations
    )


def delete_faq(faq_id):
    # First delete all the translations for
    # the FAQ id.
    FAQTranslation.objects.filter(faq__id=faq_id).delete()

    # Then delete the reference to the FAQ
    FAQ.objects.filter(id=faq_id).delete()
