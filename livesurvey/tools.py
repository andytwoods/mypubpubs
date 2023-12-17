import inspect
from collections import Counter

import numpy

from . import forms
from django.forms import Form


def get_livesurvey_forms():
    return [cls for name, cls in inspect.getmembers(forms, inspect.isclass)
            if issubclass(cls, Form)]


def get_livesurvey_form_names():
    return [name for name, cls in inspect.getmembers(forms, inspect.isclass)
            if issubclass(cls, Form)]


def get_livesurvey_form(form_name):
    found = [cls for name, cls in inspect.getmembers(forms, inspect.isclass)
            if issubclass(cls, Form) and name == form_name]
    return found[0]

def gen_bounds(_min: float, _max:float, divisions: int):
    lower_bound = _min
    difference = (_max - _min) / float(divisions)
    upper_bound = difference
    bounds = []
    while upper_bound <= _max:
        bounds.append((lower_bound, upper_bound))
        lower_bound += difference
        upper_bound += difference
    return bounds

def histogram_labels(edges):
    labels = []
    my_iterator = iter(edges)
    left = next(my_iterator)

    for right in my_iterator:
        labels.append(f'{ left } - { right }')
        left = right

    return labels
def histogram_data(data):
    bins = numpy.histogram(data, 'auto')
    bins_count = bins[0]
    bin_edges = bins[1]
    total = numpy.sum(bins_count)
    bins_percent = bins_count / total * 100

    return bins_percent.tolist(), histogram_labels(bin_edges)

def pie_data(data, choices):
    counted = Counter(data)
    total = counted.total()

    counted_list = []
    labels_list = []

    choices_dict = {key: val for key, val in choices}

    for label, val in counted.items():
        counted_list.append(val / total * 100)
        labels_list.append(choices_dict[label])
    return counted_list, labels_list

def extract_dv(data, dv):
    outcome = [d.get(dv, None) for d in data]
    return [x for x in outcome if x is not None]