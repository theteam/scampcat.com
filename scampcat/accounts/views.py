from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404


def login_error(request):
    assert False, request


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('homepage'))


def profile(request, username):
    """A users profile, currently listing public scamps.
    """
    user = get_object_or_404(User, username=username, is_active=True)
    # N.B: Pagination is provided by middleware.
    object_list = user.scamps.all()
    object_count = object_list.count()
    extra_context = {'user': user,
                     'object_list': object_list,
                     'object_count': object_count}
    return render(request, 'accounts/profile.html', extra_context)
