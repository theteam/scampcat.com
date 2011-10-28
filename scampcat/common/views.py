from django.shortcuts import render

from scampcat.common.utils import get_lolcat


def not_found_handler(request):
    """Not found url"""
    lolcat = get_lolcat()
    extra_context = {'object': lolcat}
    return render(request, '404.html', extra_context, status=404)


def error_handler(request):
    """Error url """
    lolcat = get_lolcat()
    extra_context = {'object': lolcat}
    return render(request, '500.html', extra_context, status=500)
