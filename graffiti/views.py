from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
def home(request, vr_id:str):
    return None


def img(request, vr_id:str):
    return HttpResponseRedirect()