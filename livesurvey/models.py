from django.db import models
from django.utils.text import slugify
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class Graph(models.Model):
    class GraphType(models.TextChoices):
        BAR = "BA", _("Bar chart")
        PIE = "PI", _("Pie chart")
        HISTOGRAM = "HI", _("Histogram")

    type = models.CharField(max_length=2, choices=GraphType.choices, default=GraphType.BAR)

    # dv via foreignkey(Question) related_name
    iv1 = models.ForeignKey('Question', on_delete=models.PROTECT, related_name='iv1')
    iv2 = models.ForeignKey('Question', on_delete=models.PROTECT, related_name='iv2')


class Question(models.Model):
    options = models.JSONField(default=dict)
    graph = models.ForeignKey(Graph, null=True, blank=True, on_delete=models.PROTECT, related_name='dv')
    text = models.TextField()
    survey = models.ForeignKey('Survey', on_delete=models.CASCADE, related_name='questions')


class Survey(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=32, help_text='Short title, which is used to generate the URL for the survey')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ParticipantFormData(TimeStampedModel):
    data = models.JSONField(default=dict)
    form = models.CharField(max_length=64)
    survey = models.ForeignKey('Survey', on_delete=models.CASCADE)
    session_id = models.CharField(max_length=32)

    def __str__(self):
        return self.session_id + ' ' + self.form + ' ' + str(self.data)

    @classmethod
    def update_row(cls, session_id, survey: Survey, form_name: str, form_data: dict):
        p: ParticipantFormData
        p, created = cls.objects.get_or_create(session_id=session_id, survey=survey, form=form_name)
        p.data = form_data
        p.save()

    @classmethod
    def chart_data(cls, survey: Survey, form_name):
        return  list(cls.objects.filter(survey=survey, form=form_name).values_list('data', flat=True))