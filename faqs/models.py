from django.db import models
from ckeditor.fields import RichTextField


# We'll be using ISO 639-1 language codes to store
# the languages in our tables.
class Language(models.TextChoices):
    EN = "en", "English"
    HI = "hi", "Hindi"
    BN = "bn", "Bengali"
    DE = "de", "German"
    IT = "it", "Italian"
    JA = "ja", "Japanese"


# This model basically stores the FAQ question
# and answer in the base / original language as
# noted intiailly (not translated).
class FAQ(models.Model):
    base_lang = models.CharField(choices=Language.choices)
    question = models.TextField(max_length=500)
    answer = RichTextField()
    created_at = models.DateTimeField(auto_now=True)


# This model stores the translations of each row of the
# FAQ model in each of the supported languages.
class FAQTranslation(models.Model):
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE)
    lang = models.CharField(choices=Language.choices, db_index=True)
    question = models.TextField(max_length=500)
    answer = RichTextField()

    class Meta:
        unique_together = ("faq", "lang")
        indexes = [
            models.Index(
                fields=["faq", "lang"],
                name="faq_lang_index",
            ),
            models.Index(
                fields=["lang", "question"],
                name="lang_question_index",
            ),
        ]

    def to_dict(self):
        language = dict(Language.choices).get(self.lang)

        return {
            "id": self.faq_id,
            "language": language,
            "question": self.question,
            "answer": self.answer,
        }
