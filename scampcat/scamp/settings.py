from django.conf import settings

DEFAULT_ALLOWED_MIMETYPES = {
    'image/jpeg': 'jpg',
    'image/jpg': 'jpg',
    'image/png': 'png',
    'image/gif': 'gif',
}

DEFAULT_UPLOAD_MAX_SIZE = 5242880 # bytes (5MB)

ALLOWED_MIMETYPES = getattr(settings, 'SCAMP_ALLOWED_MIMETYPES', 
                            DEFAULT_ALLOWED_MIMETYPES)

UPLOAD_MAX_SIZE = getattr(settings, 'SCAMP_UPLOAD_MAX_SIZE',
                          DEFAULT_UPLOAD_MAX_SIZE)
