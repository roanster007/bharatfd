import redis
import json

from googletrans import Translator

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from faqs.models import FAQ, FAQTranslation, Language

supported_langs = [lang.value for lang in Language]

# Redis Cache Services
redis_client = None
faq_cache_key = "faqs_en"

# Google Translate Service
translator = None


# Initializes services when the server is started
def initialize_services():
    # Initialize `googletrans` translator
    global translator
    translator = Translator()

    # Initialize redis client.
    initialize_redis_client()
    


def initialize_redis_client():
    global redis_client
    global faq_cache_key

    redis_client = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )

    # Invalidate all the old cache
    redis_client.delete(faq_cache_key)

    # We cache the FAQs in English language
    # since it is the most frequently used
    # one.
    faqs = FAQTranslation.objects.filter(lang=Language.EN)
    faq_data = [faq.to_dict() for faq in faqs]

    for faq in faq_data:
        redis_client.rpush(faq_cache_key, json.dumps(faq))



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

        # We want to cache english translation for future
        # use.
        if lang == Language.EN:
            en_translated = faq_translation.to_dict()

    await sync_to_async(FAQTranslation.objects.bulk_create, thread_sensitive=True)(
        translations
    )

    redis_client.rpush(faq_cache_key, json.dumps(en_translated))


def delete_faq(faq_id):
    # First delete all the translations for
    # the FAQ id.
    FAQTranslation.objects.filter(faq__id=faq_id).delete()

    # Then delete the reference to the FAQ
    FAQ.objects.filter(id=faq_id).delete()

    # Remove that faq from the cache
    faq_data = [json.loads(item) for item in redis_client.lrange(faq_cache_key, 0, -1)]
    redis_client.delete(faq_cache_key)

    for faq in faq_data:
        if faq.get("id") == faq_id:
            continue
        
        redis_client.rpush(faq_cache_key, json.dumps(faq))


def maybe_get_faq_data(lang):
    if lang not in supported_langs:
        return
    
    # If the requested language is `English`, use the results
    # from the cache.
    if lang == Language.EN:
        faq_data = [json.loads(item) for item in redis_client.lrange(faq_cache_key, 0, -1)]
    else:
        faqs = FAQTranslation.objects.filter(lang=lang)
        faq_data = [faq.to_dict() for faq in faqs]

    return faq_data
