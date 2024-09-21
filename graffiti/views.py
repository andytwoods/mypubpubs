from django.contrib import messages
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from throttle.decorators import throttle

from graffiti.forms import UploadImageForm
from graffiti.models import GraffitiImage, Headset, NoImage


## @login_required(login_url='/accounts/signup/')
def make_sure_img_url_is_saved_not_some_ad_to_dropbox(request, image: GraffitiImage):
    if 'dropbox' in image.url and "raw=1" not in image.url:
        sep = '?' if '?' not in image.url else '&'
        image.url += sep + "raw=1"
        message = mark_safe("We detected you uploaded a link to a dropbox image. We slightly modified "
                               "your URL (<a href='https://cantonbecker.com/etcetera/2014/how-to-directl"
                            "y-link-or-embed-dropbox-images/' target='_blank'>info</a>) so that it links to your actual"
                            " image, and not a dropbox webpage within which the image is embedded.")
        messages.info(request, message)


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
            graffiti_image = form.save(commit=False)
            messages.success(request, 'Successfully saved! You can now access your image on your headset')
            make_sure_img_url_is_saved_not_some_ad_to_dropbox(request, graffiti_image)
            graffiti_image.save()
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

NO_IMAGE_RESPONSE = 'no image'

@throttle(zone='default')
def img(request, vr_id: str):
    try:
        headset: Headset = Headset.objects.get(vr_id=vr_id)
    except Headset.DoesNotExist:
        raise Http404

    try:
        graffiti_image: GraffitiImage = GraffitiImage.retrieve_and_check_valid(headset)
    except NoImage:
        return HttpResponse(NO_IMAGE_RESPONSE)
    if graffiti_image.url:
        return HttpResponse(graffiti_image.url)
    raise Http404


@throttle(zone='default')
def code(request, vr_id: str, msg=''):
    headset = Headset.get_or_generate_code(vr_id)
    url = request.build_absolute_uri(reverse('graffiti_linkup', args=(headset.temp_code,)))
    return JsonResponse({'url': url, 'code': headset.temp_code})


def home(request):
    return render(request, 'graffiti/home.html')
