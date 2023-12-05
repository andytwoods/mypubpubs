import inspect
from . import forms
from django.forms import Form


def get_livesurvey_forms():
    return [cls for name, cls in inspect.getmembers(forms, inspect.isclass)
            if issubclass(cls, Form)]


def get_livesurvey_form_names():
    return [name for name, cls in inspect.getmembers(forms, inspect.isclass)
            if issubclass(cls, Form)]


def get_livesurvey_form(form_name):
    return [cls for name, cls in inspect.getmembers(forms, inspect.isclass)
            if issubclass(cls, Form) and name == form_name]
