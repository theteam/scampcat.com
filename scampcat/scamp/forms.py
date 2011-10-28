from __future__ import with_statement
import hashlib

from django import forms
from django.contrib.auth.models import AnonymousUser
from django.core.files.storage import default_storage
from taggit.forms import TagField

from scampcat.scamp.models import Annotation, Scamp, Image
from scampcat.scamp.settings import ALLOWED_MIMETYPES
from scampcat.scamp.utils import clone_scamp, download_and_validate_image


class AnnotationForm(forms.ModelForm):

    class Meta:
        model = Annotation
        fields = ('text', 'order', 'pos_x', 'pos_y', 'facing')

    def __init__(self, scamp, *args, **kwargs):
        self.scamp = scamp
        super(AnnotationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, **kwargs):
        annotation = super(AnnotationForm, self).save(commit=False, **kwargs)
        annotation.scamp = self.scamp
        if commit:
            annotation.save()
        return annotation


class ScampForm(forms.ModelForm):

    class Meta:
        model = Scamp
        fields = ('title', 'description')


class ScampCloneForm(forms.Form):
    """This form handles the cloning of a scamp;
    it also checks whether the scamp was actually
    cloneable.
    """
    scamp_to_clone = forms.IntegerField(min_value=1)

    def __init__(self, user, *args, **kwargs):
        """We need the user for saving purposes later.
        """
        self.user = user
        super(ScampCloneForm, self).__init__(*args, **kwargs)

    def clean_scamp_to_clone(self):
        """Make sure the scamp exists and is cloneable
        before trying to do so.
        """
        scamp_id = self.cleaned_data.get('scamp_to_clone')
        try:
            self.scamp = Scamp.objects.get(pk=scamp_id)
        except Scamp.DoesNotExist:
            raise forms.ValidationError("Scamp does not exist to clone.")
        else:
            if not self.scamp.is_cloneable:
                raise forms.ValidationError("Scamp is not cloneable.")
        return scamp_id

    def save(self, *args, **kwargs):
        """Carry out the cloning process and return the
        new scamp clone.
        """
        return clone_scamp(self.scamp, self.user)


class ScampUploadForm(forms.Form):
    """Form to upload an image from the local file
    system or download it via a URL. Also handles
    all the saving of said image.:
    """
    image = forms.ImageField(required=False, label="Upload from disk")
    url = forms.URLField(verify_exists=False, required=False,
                         label="Link to one")

    def __init__(self, user=None, *args, **kwargs):
        if isinstance(user, AnonymousUser):
            self.user = None
        else:
            self.user = user
        super(ScampUploadForm, self).__init__(*args, **kwargs)

    def clean_image(self):
        """Check the image is of a supported type.
        """
        image = self.cleaned_data.get('image')
        if image and not image.content_type in ALLOWED_MIMETYPES:
            types = "/".join([x for x in ALLOWED_MIMETYPES.itervalues()])
            error = "Image is not of an allowed type:  %s." % types
            raise forms.ValidationError(error)
        return image

    def clean_url(self):
        """Access the URL provided and downloads the contents,
        only returns fine if the file provided is an image.
        """
        url = self.cleaned_data.get('url')
        if url:
            self.cleaned_image_data = download_and_validate_image(url)
            if not self.cleaned_image_data['image']:
                error = "%s" % self.cleaned_image_data['message']
                raise forms.ValidationError(error)
        return url

    def clean(self):
        image_provided = self.cleaned_data.get('image')
        url_provided = self.cleaned_data.get('url')
        if image_provided and url_provided:
            raise forms.ValidationError('Please only provide either a file '
                                        '*or* a URL.')
        elif image_provided or url_provided:
            # This is the result we want, only one
            # of the two fields filled out.
            return self.cleaned_data
        else:
            raise forms.ValidationError('You must provide an image or a URL.')

    def save(self, commit=True, *args, **kwargs):
        """Creates the relevant scamp and image instances
        and saves them to the db if commit is True.
        """
        image_data = {}
        image_field = self.cleaned_data.get('image')
        if image_field:
            # Determine the filehash
            file_hash = hashlib.md5()
            # Make sure we don't choke python with a big file
            # Take advantage of the fact that MD5 has 128-byte digest blocks
            for chunk in iter(lambda: image_field.read(128), ''):
                file_hash.update(chunk)
            image_data['url_key'] = file_hash.hexdigest()
            save_path = 'scamp-images/%s.%s' % (image_data['url_key'],
                                ALLOWED_MIMETYPES[image_field.content_type])
            if default_storage.exists(save_path):
                # File exists, associate this image
                image_file = save_path
            else:
                # File doesn't exist, save it
                image_file = default_storage.save(save_path, image_field)
            image_data['image'] = image_file
        else:
            url = self.cleaned_data.get('url')
            image_data['url_key'] = hashlib.md5(url).hexdigest()
            image_data['url'] = url
            save_path = 'scamp-images/%s.%s' % (
                                          image_data['url_key'],
                                          self.cleaned_image_data['filetype'])
            if default_storage.exists(save_path):
                # File exists, associate this image
                image_file = save_path
            else:
                image_file = default_storage.save(
                    save_path, self.cleaned_image_data['image'])
            image_data['image'] = image_file
        # Create the image instance.
        image = Image(**image_data)
        if commit:
            image.save()

        # Create the scamp instance and attach the image.
        scamp_data = {'image': image}
        if self.user:
            scamp_data['user'] = self.user
        scamp = Scamp(**scamp_data)
        if commit:
            scamp.save()
        return scamp, image


class ScampTagsForm(forms.Form):
    """Form to tag a ``Scamp``"""
    tags = TagField()
