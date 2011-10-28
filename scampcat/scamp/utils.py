import cStringIO
import Image
from hashlib import md5

import requests
from django.conf import settings
from django.core.files.base import ContentFile

from scampcat.scamp.models import Scamp
from scampcat.scamp.settings import ALLOWED_MIMETYPES, UPLOAD_MAX_SIZE


def clone_scamp(scamp, user):
    """Given an existening scamp, this method creates a replica
    including all relevant attachments and returns the clone.
    """
    data = {'title': scamp.title,
            'description': scamp.description,
            'image': scamp.image
    }
    if user.is_authenticated():
        data['user'] = user
    new_scamp = Scamp.objects.create(**data)
    # Now that we have the recreated the Scamp,
    # we must also duplicate everything that was
    # attached to it. Tags & Annotations.
    old_tags = [tag.name for tag in scamp.tags.all()]
    new_scamp.tags.set(*old_tags)
    annotation_list = scamp.annotations.all()
    for annotation in annotation_list:
        annotation_data = {'text': annotation.text,
                           'order': annotation.order,
                           'pos_x': annotation.pos_x,
                           'pos_y': annotation.pos_y,
                           'facing': annotation.facing,
        }
        new_scamp.annotations.create(**annotation_data)
    # Return the CLONED scamp.
    return new_scamp


def coerce_put_post(request):
    """Django doesn't have coerce PUT requests into
    a query dict, therefore we force it here.
    """
    request.method = "POST"
    request._load_post_and_files()
    request.method = "PUT"
    request.PUT = request.POST


def get_image_key(url):
    """Generates a unique id from a given url, factored
    out into a separate method just incase we need to change
    it in the future."""
    return md5(url).hexdigest()


def download_and_validate_image(url, temp_folder=None):
    """Tries to download and save a given URL to a temporary
    location, checking it is a valid image using PIL. For
    small images we simply save to a memory buffer, for
    larger images, we take the safe option of saving them
    to disk first.
    """
    ret_dict = {'image': '',
                'filetype': '',
                'mimetype': '',
                'message': ''}
    if temp_folder is None:
        temp_folder = settings.FILE_UPLOAD_TEMP_DIR
    req = requests.get(url)
    if not req.ok:
        error_messages = {404: "The image could not be found.",
                          410: "The server says the image has been removed.",
                          500: "There was an error with the remote server."}
        msg = error_messages.get(req.status_code, "An unknown error occured.")
        ret_dict['message'] = "Sorry, the image retrieval failed. %s" % msg
        return ret_dict
    mimetype = req.headers['content-type']
    if mimetype not in ALLOWED_MIMETYPES:
        ret_dict['message'] = "Image is not of an allowed type: %s." % \
                    "/".join([x for x in ALLOWED_MIMETYPES.itervalues()])
        return ret_dict
    if len(req.content) > UPLOAD_MAX_SIZE:
        ret_dict['message'] = "The image exceeds our maximum allowed size" \
                      " of %s bytes." % UPLOAD_MAX_SIZE
        return ret_dict
    try:
        # To test it's actually an image we can use, we translate 
        # to an in memory IOString  and try an open with PIL.
        buffer = cStringIO.StringIO(req.content)
        buffered_image = Image.open(buffer)
    except IOError:
        ret_dict['message'] = "We are unable to open the image, is it corrupt?"
        return ret_dict
    else:
        ret_dict.update({'image': ContentFile(req.content),
                        'filetype': ALLOWED_MIMETYPES[mimetype],
                        'mimetype': mimetype,
                        'message': 'Success'})
        return ret_dict
