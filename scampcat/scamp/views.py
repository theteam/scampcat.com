from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.http import (HttpResponseForbidden, HttpResponseRedirect, Http404,
                         HttpResponseNotAllowed)
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import View, DetailView
from taggit.utils import edit_string_for_tags

from scampcat.scamp.models import Scamp, Annotation
from scampcat.scamp.emitters import json_response
from scampcat.scamp.forms import (AnnotationForm, ScampForm, ScampCloneForm,
                                  ScampUploadForm, ScampTagsForm)
from scampcat.scamp.sessions import set_scamp_session
from scampcat.scamp.utils import coerce_put_post


def homepage(request):
    """Upload page for the scamp; handles the POST
    request for either uploading an image or linking to one.
    """
    if request.method == 'POST':
        form = ScampUploadForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            scamp, image = form.save()
            # The ``scamp_key`` session key is a list of scamp keys
            # (uid's on the scamp) that can be edited by the user with
            # that active session. The only other way a user can edit
            # a scamp is if they are logged in and owner of that scamp.
            set_scamp_session(request, scamp)
            return HttpResponseRedirect(scamp.get_absolute_url())
    else:
        form = ScampUploadForm()
    extra_context = {'form': form}
    return render(request, 'homepage.html', extra_context)


class ScampDetailView(DetailView):
    """Classed based view to render the scamp details"""
    context_object_name = 'object'

    def get_object(self):
        obj = get_object_or_404(Scamp, slug=self.kwargs['slug'])
        return obj

    def get_context_data(self, **kwargs):
        context = super(ScampDetailView, self).get_context_data(**kwargs)
        if self.object.is_editable(self.request.user,
                                   self.request.session.get('scamp_key')):
            context['editable'] = True
        else:
            context['editable'] = False
        return context

    def post(self, request, *args, **kwargs):
        """POSTing to this view is used to update attributes
        on the scamp such as the title and description.
        """
        self.object = self.get_object()
        form = ScampForm(request.POST, instance=self.object)
        if self.object.is_editable(request.user,
                                   request.session.get('scamp_key')):
            if form.is_valid():
                scamp = form.save()
                response = {'title': scamp.title,
                            'description': scamp.description.rendered,
                            'description_raw': scamp.description.raw,
                }
                return json_response(200, **response)
            else:
                return json_response(400, message=form.errors.as_ul())
        else:
            return json_response(403, message="Permission denied.")

    def put(self, request, *args, **kwargs):
        """PUTing to this view is used to create
        a specific annotation which is attached
        to the scamp at this URL.
        """
        # Due to Django's handling of PUT requests
        # we have to coerce our PUT variables via
        # the POST handling stuff first.
        coerce_put_post(request)
        self.object = self.get_object()
        form = AnnotationForm(self.object, request.PUT)
        if self.object.is_editable(request.user,
                                   request.session.get('scamp_key')):
            if form.is_valid():
                annotation = form.save()
                response = {'id': annotation.id,
                            'text_raw': annotation.text.raw,
                            'text_rendered': annotation.text.rendered,
                            'edit_url': reverse('annotation_detail',
                                                args=[self.object.slug,
                                                      annotation.id])}
                return json_response(200, **response)
            else:
                return json_response(400, message=form.errors.as_ul())
        else:
            return json_response(403, message="Permission denied.")


class AnnotationDetailView(DetailView):

    def get_object(self):
        obj = get_object_or_404(Annotation,
                                scamp__slug=self.kwargs['scamp_slug'],
                                id=self.kwargs['annotation_id'])
        return obj

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        """POSTing here updates a specific existing annotation.
        """
        self.object = self.get_object()
        form = AnnotationForm(self.object.scamp, request.POST,
                                  instance=self.object)
        if self.object.scamp.is_editable(request.user,
                                         request.session.get('scamp_key')):
            if form.is_valid():
                annotation = form.save()
                response = {'id': annotation.id,
                            'text_rendered': annotation.text.rendered}
                return json_response(200, **response)
            else:
                return json_response(400, message=form.errors.as_ul())
        else:
            return json_response(403, message="Permission denied.")

    def delete(self, request, *args, **kwargs):
        """DELETEing here deletes a specific existing annotation.
        """
        self.object = self.get_object()
        if self.object.scamp.is_editable(request.user,
                                         request.session.get('scamp_key')):
            self.object.delete()
            return json_response(200)
        else:
            return json_response(403, message="Permission denied.")


class ScampReorderView(View):
    """Provides the API for reordering of annotations
    on a specific scamp.
    """

    def get_object(self):
        obj = get_object_or_404(Scamp, slug=self.kwargs['slug'])
        return obj

    def get(self, request, *args, **kwargs):
        """Currently this is a POST only view so
        we return an http 405.
        """
        return HttpResponseNotAllowed()

    def post(self, request, *args, **kwargs):
        """Post a list of ordered annotation IDs to
        this view to get them reordered on the scamp.
        """
        self.object = self.get_object()
        if self.object.is_editable(request.user,
                                   request.session.get('scamp_key')):
            new_order = request.POST.getlist('order')
            new_order = [int(x) for x in new_order]
            old_order = self.object.annotations.all().values_list('id',
                                                                  flat=True)
            # Check we have the same IDs before and
            # after before we start reordering.
            if set(new_order) == set(old_order):
                for i, pk in enumerate(new_order):
                    Annotation.objects.filter(pk=pk).update(order=i+1)
                return json_response(200)
            else:
                return json_response(400,
                                     message="IDs sent for reordering do"
                                        " not match those already saved.")
        else:
            return json_response(403, message="Permission denied.")


def scamp_add_tags(request, slug):
    """Helps to tags the ``Scamp``"""
    scamp = get_object_or_404(Scamp, slug=slug)
    if request.method == 'POST':
        form = ScampTagsForm(request.POST)
        if form.is_valid():
            form.cleaned_data['tags']
            scamp.tags.set(*form.cleaned_data['tags'])
        return HttpResponseRedirect(scamp.get_absolute_url())
    else:
        tags = edit_string_for_tags([o for o in scamp.tags.all()])
        if tags:
            form = ScampTagsForm({'tags': tags})
        else:
            form = ScampTagsForm()
    extra_context = {'form': form,
                     'object': scamp}
    return render(request, 'scamp/scamp_tags.html', extra_context)


@login_required
def scamp_claim(request, slug):
    """Allows a user to claim an anonymous scamp and
    attach it to the account that they are logged into.
    """
    scamp = get_object_or_404(Scamp, slug=slug)
    if scamp.is_editable(request.user,
                         request.session.get('scamp_key')):
        # The scamp is editable, either because it's attached to the
        # logged in user or because the scamp key is set on their session
        # key. Therefore if the scamp is not attached to a user, we know
        # the user is logged in (due to the decorator_ so we can safely
        # attach it to the user.
        if not scamp.user:
            scamp.user = request.user
            scamp.save()
            messages.success(request,
                             _("This Scamp is now attached to your account."))
        else:
            messages.warning(request,
                             _("This Scamp is already attaced to another "
                               "account."))
    else:
        messages.error(request,
                       _("You do not have permission to claim this Scamp."))
    url = scamp.get_absolute_url()
    return HttpResponseRedirect(url)


@require_POST
def scamp_clone(request, slug):
    """Clones the current Scamp and everything
    relevent that is attached to it.
    """
    scamp = get_object_or_404(Scamp, slug=slug)
    form = ScampCloneForm(request.user, {'scamp_to_clone': scamp.id})
    if form.is_valid():
        new_scamp = form.save()
        set_scamp_session(request, new_scamp)
        messages.success(request, _("Scamp cloned succesfully!"))
        return HttpResponseRedirect(new_scamp.get_absolute_url())
    else:
        return HttpResponseForbidden()


def scamp_delete(request, slug):
    """Scamp delete view, handles confirmation
    and the deletion.
    """
    scamp = get_object_or_404(Scamp, slug=slug)
    if request.method == 'POST':
        if scamp.is_editable(request.user,
                             request.session.get('scamp_key')):
            scamp.delete()
            messages.success(request, _("The Scamp was deleted succesfully."))
            if request.user.is_authenticated():
                url = reverse('accounts_profile', args=[request.user.username])
            else:
                url = reverse('homepage')
            return HttpResponseRedirect(url)
        else:
            messages.error(request, _("You do not have permission to delete "
                                      "this Scamp."))
        return HttpResponseRedirect(scamp.get_absolute_url())
    context = {'object': scamp}
    return render(request, 'scamp/scamp_delete.html', context)


@login_required
def scamp_report(request, slug):
    """Reports an ``Scamp`` as inappropriate"""
    scamp = get_object_or_404(Scamp, slug=slug)
    if request.method == 'POST':
        site = Site.objects.get_current()
        context = {'user': request.user,
                   'site': site,
                   'EMAIL_SUBJECT_PREFIX': settings.EMAIL_SUBJECT_PREFIX,
                   'object': scamp,
        }
        subject = render_to_string('scamp/email/subject.txt', context)
        subject = ''.join(subject.splitlines())
        message = render_to_string('scamp/email/message.txt', context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  [settings.SCAMP_MANAGER])
        messages.success(request, _("The Scamp has been reported for "
                                    "violation of terms, thank you."))
    return HttpResponseRedirect(scamp.get_absolute_url())


def scamp_tags(request, tag):
    """Helps to tags the ``Scamp``"""
    tag_list = tag.split('+')
    object_list = Scamp.objects.filter(tags__name__in=tag_list)
    extra_context = {'object_list': object_list,
                     'tag_list': tag_list}
    return render(request, 'scamp/scamp_list_tags.html', extra_context)


@require_POST
def scamp_toggle_lock(request, slug):
    """Toggles a scamps editable status"""
    scamp = get_object_or_404(Scamp, slug=slug)
    if scamp.is_editable(request.user,
                         request.session.get('scamp_key')):
        scamp.is_locked = False if scamp.is_locked else True
        scamp.save()
        message = _('Scamp locked for editing.') if scamp.is_locked else \
                  _('Scamp unlocked for editing.')
        messages.success(request, message)
    return HttpResponseRedirect(scamp.get_absolute_url())
