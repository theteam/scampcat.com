from django.contrib.sites.models import Site

from scampcat.scamp.models import Scamp
from piston.handler import BaseHandler


class LiberationHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        site = Site.objects.get_current()
        if not request.user.is_authenticated():
            return []
        scamp_list = Scamp.objects.select_related(depth=2).\
            filter(user=request.user)
        object_list = []
        for scamp in scamp_list:
            data = {'title': scamp.title,
                    'description': scamp.description,
                    'created': scamp.created,
                    'modified': scamp.modified,
                    'tags': [tag.name for tag in scamp.tags.all()],
                    'url': 'http://%s%s' % (site.domain,
                                            scamp.get_absolute_url(),)
            }
            data_image = {'created': scamp.image.created,
                          'modified': scamp.image.modified,
                          'height': scamp.image.height,
                          'width': scamp.image.width,
                          'url': scamp.image.image.url
            }
            data['image'] = data_image
            data['annotations'] = []
            for annotation in scamp.annotations.all():
                annotation_data = {'text': annotation.text,
                                   'order': annotation.order,
                                   'pos_x': annotation.pos_x,
                                   'pos_y': annotation.pos_y,
                                   'facing': annotation.facing,
                               }
                data['annotations'].append(annotation_data)
            object_list.append(data)
        return object_list
