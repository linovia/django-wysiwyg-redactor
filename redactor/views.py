import os

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.http import urlquote
from django.utils import simplejson as json

from redactor.forms import ImageForm


UPLOAD_PATH = getattr(settings, 'REDACTOR_UPLOAD', 'redactor/')


@csrf_exempt
@require_POST
@user_passes_test(lambda u: u.is_staff)
def redactor_upload(request, upload_to=None, form_class=ImageForm, response=lambda name, url: url):
    form = form_class(request.POST, request.FILES)
    if form.is_valid():
        file_ = form.cleaned_data['file']
        path = os.path.join(upload_to or UPLOAD_PATH, file_.name)
        real_path = default_storage.save(path, file_)
        url = os.path.join(settings.MEDIA_URL, real_path)
        return HttpResponse('{ "filelink": "' + urlquote(url) + '" }')
    return HttpResponse(status=403)


@user_passes_test(lambda u: u.is_staff)
def recent_photos(request, upload_to=None):
    path = upload_to or UPLOAD_PATH
    files = [urlquote(os.path.join(settings.MEDIA_URL, path, f))
        for f in default_storage.listdir(path)[1]]
    images = [{"thumb": url, "image": url} for url in files]
    return HttpResponse(json.dumps(images), mimetype="application/json")
