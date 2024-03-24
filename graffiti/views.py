from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils.timezone import now
from throttle.decorators import throttle

from graffiti.forms import UploadImageForm
from graffiti.models import GraffitiImage, image_expires_after_x_minutes, mb_limit, Headset, NoImage


@login_required(login_url='/accounts/signup/')
@throttle(zone='default')
def linkup(request, temp_code: str):

    if not Headset.check_short_code(temp_code):
        raise Http404

    try:
        headset = Headset.objects.get(temp_code=temp_code)
    except Headset.DoesNotExist:
        raise Http404
    if headset.user is None:
        headset.user = request.user
        headset.save()

    graffiti_image, created = GraffitiImage.objects.get_or_create(headset=headset)
    if created:
        graffiti_image.save()

    form = None

    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get("image")
            if graffiti_image.image:
                storage = graffiti_image.image.storage
                if storage.exists(graffiti_image.image.name):
                    storage.delete(graffiti_image.image.name)

            graffiti_image.image = image
            graffiti_image.save()
            messages.success(request, 'Successfully uploaded your image! You can access it now on your headset')
            form = None

    if not form:
        form = UploadImageForm()
    image_file = graffiti_image.image.url if graffiti_image and graffiti_image.image else None

    if image_file:
        time_left_til_deleted = int(
            (timedelta(minutes=image_expires_after_x_minutes) - (now() - graffiti_image.created)).
            total_seconds()) if image_file else ''
    else:
        time_left_til_deleted = None

    context = {
        'form': form,
        'image_file': image_file,
        'image': graffiti_image.image if graffiti_image else None,
        'time_til_deleted': image_expires_after_x_minutes,
        'max_mb': mb_limit,
        'time_left_til_deleted': time_left_til_deleted
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
