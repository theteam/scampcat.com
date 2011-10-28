from django.db import models
from django.utils.translation import ugettext as _

from markitup.fields import MarkupField
from taggit.managers import TaggableManager

from scampcat.common.models import TimestampAbstract
from scampcat.common.utils import generate_random_string
from scampcat.common.baseconv import shortie


class Set(TimestampAbstract):
    """Links a set of scamps together.
    """
    user = models.ForeignKey('auth.User', related_name="sets")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    description = MarkupField()
    scamps = models.ManyToManyField('scamp.Scamp', related_name="sets")

    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']

    def __unicode__(self):
        return u"Set: %s" % self.title


class Scamp(TimestampAbstract):
    """A board for which to anchor the image
    and annotations to.
    """
    user = models.ForeignKey('auth.User', related_name="scamps",
                             null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=100, unique=True, editable=False)
    description = MarkupField(blank=True)
    image = models.ForeignKey('scamp.Image', related_name="scamps", null=True,
                              on_delete=models.SET_NULL)
    is_cloneable = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    # Used as an unknown/unguessable identifier.
    key = models.CharField(max_length=32, unique=True, editable=False)
    tags = TaggableManager(blank=True)

    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']

    def __unicode__(self):
        return u"Scamp: %s" % self.title if self.title else self.slug

    @models.permalink
    def get_absolute_url(self):
        return ('scamp_detail', [self.slug, ])

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_random_string(32)
        # We do this because we don't have the id before we
        # save the instance, and we need that for the slug.
        has_slug = True if self.slug else False
        if not has_slug:
            # We need to save something in the slug field for
            # the time being to get around the unique constraint.
            self.slug = self.image.image
        super(Scamp, self).save(*args, **kwargs)
        # Now that we have an id we can regenerate the
        # slug based upon this and save again.
        if not has_slug:
            self.slug = shortie.from_decimal(self.id)
            self.save()

    def is_editable(self, user=None, given_keys=None):
        """Checks wheter this Scamp can be edited
        by eitehr passing a user or a key.
        """
        if given_keys is None:
            given_keys = []
        if user == self.user or self.key in given_keys:
            return True
        return False


class Image(TimestampAbstract):
    """A simple model which represents an image while
    caching width/height fields and also storing URL meta
    for use when we're grabbing images by URL.
    """
    image = models.ImageField(max_length=255, upload_to='scamp-images')
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    url = models.URLField(max_length=255, verify_exists=False, blank=True)
    url_key = models.CharField(max_length=32, blank=True)

    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']

    def __unicode__(self):
        return u"Image: %s" % (self.id)

    def save(self, *args, **kwargs):
        self.width = self.image.width
        self.height = self.image.height
        super(Image, self).save(*args, **kwargs)


class Annotation(TimestampAbstract):
    """An annotation is a snippet of text
    which gets anchored to a scamp (and
    therefore an image)
    """
    NORTH, EAST, SOUTH, WEST = 0, 90, 180, 270
    FACING_CHOICES = (
        (NORTH, _('North')),
        (EAST, _('East')),
        (SOUTH, _('South')),
        (WEST, _('West')),
    )

    scamp = models.ForeignKey('scamp.Scamp', related_name="annotations")
    text = MarkupField()
    order = models.PositiveIntegerField()
    pos_x = models.DecimalField(max_digits=6, decimal_places=3, default='0')
    pos_y = models.DecimalField(max_digits=6, decimal_places=3, default='0')
    facing = models.PositiveIntegerField(choices=FACING_CHOICES)

    class Meta:
        get_latest_by = 'created'
        ordering = ['order']

    def __unicode(self):
        return u"Scamp: %s, Annotation %s" % (self.scamp, self.order)

    @models.permalink
    def get_absolute_url(self):
        return ('annotation_detail', [self.scamp.slug, self.id])
