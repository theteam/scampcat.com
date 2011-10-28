import json

from django.http import HttpResponse


def json_response(status=200, message=None, **kwargs):
    # Set a default message if none provided.
    success_codes = [200, 201]
    if message is None:
        message = "Success" if status in success_codes else "Error"
    # Create the json dictionary.
    return_dict = {'success': True if status in success_codes else False,
                   'message': message}
    return_dict.update(**kwargs)
    content = json.dumps(return_dict)
    return HttpResponse(content, mimetype="application/json", status=status)
