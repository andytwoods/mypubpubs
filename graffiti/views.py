from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib import messages
from throttle.decorators import throttle

from graffiti.forms import UploadImageForm
from graffiti.models import GraffitiImage


@login_required
@throttle(zone='default')
def upload(request, vr_id: str):
    graffiti_image: GraffitiImage = GraffitiImage.objects.filter(vr_id=vr_id).first()
    form = None
    if not graffiti_image:
        graffiti_image = GraffitiImage(vr_id=vr_id)
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
    image_file = graffiti_image.image.url if graffiti_image.image else ''

    context = {
        'form': form,
        'image_file': image_file,
        'image': graffiti_image.image,
    }
    return render(request, 'graffiti/upload_image.html', context)


@throttle(zone='default')
def get_headset_id(headset_id: str):
    return JsonResponse({'headset_id': headset_id})


@throttle(zone='default')
def img(request, vr_id: str):
    graffiti_image: GraffitiImage = GraffitiImage.objects.filter(vr_id=vr_id).first()
    if graffiti_image.image and graffiti_image.image.url:
        return HttpResponseRedirect(graffiti_image.image.url)
    raise Http404


@throttle(zone='default')
def code(request, vr_id: str):
    code: str = GraffitiImage.get_or_generate_code(vr_id)
    return HttpResponse()


def home(request):
    return render(request, 'graffiti/home.html')
