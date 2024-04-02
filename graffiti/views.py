from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import now
from throttle.decorators import throttle

from graffiti.forms import UploadImageForm
from graffiti.models import GraffitiImage, image_expires_after_x_minutes, mb_limit, Headset, NoImage


## @login_required(login_url='/accounts/signup/')
@throttle(zone='default')
def linkup(request, temp_code: str):

    if not Headset.check_short_code(temp_code):
        return render(request, 'graffiti/headset_not_contacted_backend.html')

    try:
        headset = Headset.objects.get(temp_code=temp_code)
    except Headset.DoesNotExist:
        return render(request, 'graffiti/headset_not_contacted_backend.html')
    if headset.user is None and not request.user.is_anonymous:
        headset.user = request.user
        headset.save()

    graffiti_image, created = GraffitiImage.objects.get_or_create(headset=headset)
    if created:
        graffiti_image.save()

    if request.htmx:
        graffiti_image.delete()
        headset.delete()
        response = HttpResponse()
        messages.success(request, 'Successfully deleted data')
        response["HX-Redirect"] = reverse('graffiti_home')
        return response

    form = None

    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES, instance=graffiti_image)
        if form.is_valid():
            image = form.cleaned_data.get("image")
            graffiti_image.image = image
            graffiti_image.save()
            messages.success(request, 'Successfully uploaded your image! You can access it now on your headset')
            form = None

    if not form:
        form = UploadImageForm(instance=graffiti_image)


    context = {
        'form': form,
    }
    return render(request, 'graffiti/upload_image.html', context)


@throttle(zone='default')
def get_headset_id(headset_id: str):
    return JsonResponse({'headset_id': headset_id})


@throttle(zone='default')
def img(request, vr_id: str):
    headset: Headset = Headset.objects.get(id=vr_id)
    if not headset:
        raise Http404
    try:
        graffiti_image: GraffitiImage = GraffitiImage.retrieve_and_check_valid(vr_id)
    except NoImage:
            return HttpResponse('no image')
    if graffiti_image.image and graffiti_image.image.url:
        return HttpResponseRedirect(graffiti_image.image.url)
    raise Http404


@throttle(zone='default')
def code(request, vr_id: str, msg=''):
    headset = Headset.get_or_generate_code(vr_id)
    return JsonResponse({'code': headset.temp_code, 'member': True if headset.user else False})


def home(request):
    return render(request, 'graffiti/home.html')
