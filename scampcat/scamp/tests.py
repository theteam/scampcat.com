import json
import os
from decimal import Decimal

from django.core.urlresolvers import reverse
from django.test import TestCase

from scampcat.scamp.models import Annotation, Scamp

here = lambda *x: os.path.join(os.path.dirname(os.path.realpath(__file__)), *x)


class ScampTest(TestCase):
    """Test our scamps man..
    """
    fixtures = ['accounts/test/auth.json',
                'scamp/test/scamp.json']

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_anonymous_image_upload(self):
        """Test that a non-authed user can
        submit a scamp and retain editing rights.
        """
        url = reverse('homepage')
        test_image = open(here('fixtures/scamp/test/image.jpg'))
        response = self.client.post(url, {'image': test_image})
        test_image.close()
        # Test we redirect to the scamp_detail page.
        self.assertEquals(response.status_code, 302)
        # Test that the session cookie was set because this
        # is an anonymous upload that set a session key.
        self.assertEquals(len(response.cookies), 1)
        # Test that there is now one scamp in our db.
        scamp_count = Scamp.objects.filter(user=None).count()
        self.assertEquals(scamp_count, 2) # One from fixture, one new.
        # Test the database scamp.
        scamp = Scamp.objects.all()[0]
        self.assertEquals(scamp.user, None)
        self.assertEquals(len(scamp.key), 32)
        # Follow the redirect and test we get a 200.
        redirect_to = response._headers['location'][1]
        response = self.client.get(redirect_to)
        self.assertEquals(response.status_code, 200)
        # Check that the view has worked out we're 
        # allowed to edit this thing despite not being
        # logged in.
        self.assertTrue(response.context['editable'])


    def test_user_image_upload(self):
        url = reverse('homepage')
        self.client.login(username='admin', password='theteam')
        test_image = open(here('fixtures/scamp/test/image2.jpg'))
        response = self.client.post(url, {'image': test_image})
        test_image.close()
        # Test we redirect to the scamp_detail page.
        self.assertEquals(response.status_code, 302)
        # Test that there is now one scamp in our db.
        scamp_count = Scamp.objects.filter(user__isnull=False).count()
        self.assertEquals(scamp_count, 2) # One from fixture, one new.
        scamp = Scamp.objects.all()[0]
        self.assertEquals(scamp.user.username, 'admin')
        # Follow the redirect and test we get a 200.
        redirect_to = response._headers['location'][1]
        response = self.client.get(redirect_to)
        self.assertEquals(response.status_code, 200)
        # Check that the view has worked out we're 
        # allowed to edit this thing despite not being
        # logged in.
        self.assertTrue(response.context['editable'])

    def test_failed_upload(self):
        """Test a range of what should be form failures.
        """
        url = reverse('homepage')
        response = self.client.post(url, {})
        self.assertFormError(response, 'form', '', 'You must provide an image or a URL')

    def test_edit_scamp(self):
        """Test editing of scamp.
        """
        scamp = Scamp.objects.get(id=1) # From fixture. Has attached user.
        markdown = '**This** is *raw* markdown.'
        edit_post = {
                    'title': 'Test Edited Scamp',
                    'description': markdown,
                }
        # Let's first try without logging, should fail.
        response = self.client.post(scamp.get_absolute_url(), edit_post)
        self.assertEquals(response.status_code, 403)
        # Now let's login and we should be able to attach the
        # annotation message.
        self.client.login(username='admin', password='theteam')
        response = self.client.post(scamp.get_absolute_url(), edit_post)
        self.assertEquals(response.status_code, 200)
        ret = json.loads(response.content)
        self.assertEquals(ret['success'], True)
        self.assertEquals(ret['message'], 'Success')
        self.assertEquals(ret['description'], '<p><strong>This</strong> is <em>raw</em> markdown.</p>')
        # Check the scamp has been updated (have to re-pull from db).
        scamp = Scamp.objects.get(id=1)
        self.assertEquals(scamp.description.raw, markdown)

    def test_annotation_creation(self):
        """Test creation of annotation points.
        """
        scamp = Scamp.objects.get(id=1) # From fixture. Has attached user.
        markdown = '[This](http://www.google.com) is a link *bitch*.'
        annotation_post = {
                    'order': 2,
                    'pos_x': 20.0,
                    'pos_y': 10.333,
                    'text': markdown,
                }
        # Let's first try without logging, should fail. Notice, put not post!
        response = self.client.put(scamp.get_absolute_url(), annotation_post)
        self.assertEquals(response.status_code, 403)
        # Now let's login and we should be able to attach the
        # annotation message.
        self.client.login(username='admin', password='theteam')
        response = self.client.put(scamp.get_absolute_url(), annotation_post)
        # But aha, it should fail because we're missing the facing field!
        self.assertEquals(response.status_code, 400)
        annotation_post['facing'] = 269
        response = self.client.put(scamp.get_absolute_url(), annotation_post)
        # But aha x2, 269 isn't a valid value for that the facing field.
        self.assertEquals(response.status_code, 400)
        annotation_post['facing'] = 270
        response = self.client.put(scamp.get_absolute_url(), annotation_post)
        # Now we should be cool. 
        self.assertEquals(response.status_code, 200) 
        ret = json.loads(response.content)
        self.assertEquals(ret['success'], True)
        self.assertEquals(ret['message'], 'Success')
        self.assertEquals(ret['text_rendered'], '<p><a href="http://www.google.com">This</a> is a link <em>bitch</em>.</p>')
        # Now we test the new annotation is sat in the database.
        annotations = scamp.annotations.all()
        self.assertEquals(len(annotations), 2) # One was already there in the fixtures.
        annotation = annotations[1] # It should be returned as the 2nd result due to order.
        self.assertEquals(annotation.text.raw, markdown)
        self.assertEquals(annotation.order, 2)
        self.assertEquals(annotation.pos_x, Decimal('20'))
        self.assertEquals(annotation.pos_y, Decimal('10.333'))
        self.assertEquals(annotation.facing, 270)


    def test_annotation_editing(self):
        """Test editing of annotation points.
        """
        scamp = Scamp.objects.get(id=1) # From fixture. Has attached user.
        annotation = scamp.annotations.all()[0]
        post_url = annotation.get_absolute_url()
        edited_markdown = '[This](http://www.example.com) is a rubbish link.'
        annotation_edit_post = {
                    'order': 2,
                    'pos_x': 14.5,
                    'pos_y': 20,
                    'text': edited_markdown,
                    'facing': 140,
                }
        # Let's first try without logging, should fail.
        response = self.client.post(post_url, annotation_edit_post)
        self.assertEquals(response.status_code, 403)
        # Now let's login and try again.
        self.client.login(username='admin', password='theteam')
        response = self.client.post(post_url, annotation_edit_post)
        # But aha, it should fail because the facing field is incorrect.
        self.assertEquals(response.status_code, 400)
        annotation_edit_post['facing'] = 180
        # Now we should be cool.
        response = self.client.post(post_url, annotation_edit_post)
        self.assertEquals(response.status_code, 200)
        ret = json.loads(response.content)
        self.assertEquals(ret['success'], True)
        self.assertEquals(ret['message'], 'Success')
        self.assertEquals(ret['text_rendered'], '<p><a href="http://www.example.com">This</a> is a rubbish link.</p>')
        # Now we re-pull the annotation and test we changed it.
        annotations = scamp.annotations.all()
        self.assertEquals(len(annotations), 1)
        annotation = annotations[0]
        self.assertEquals(annotation.text.raw, edited_markdown)
        self.assertEquals(annotation.order, 2)
        self.assertEquals(annotation.pos_x, Decimal('14.5'))
        self.assertEquals(annotation.pos_y, Decimal('20'))
        self.assertEquals(annotation.facing, 180)

    def test_annotation_deletion(self):
        """Test deleting the annotation points.
        """
        scamp = Scamp.objects.get(id=1)
        annotations = scamp.annotations.all()
        self.assertEquals(annotations.count(), 1)
        annotation = annotations[0]
        delete_url = annotation.get_absolute_url()
        # Try and delete without being logged in.
        response = self.client.delete(delete_url)
        self.assertEquals(response.status_code, 403)
        # Try again, logged in this time.
        self.client.login(username='admin', password='theteam')
        response = self.client.delete(delete_url)
        self.assertEquals(response.status_code, 200)
        ret = json.loads(response.content)
        self.assertEquals(ret['success'], True)
        self.assertEquals(ret['message'], 'Success')
        # Test it's wiped from the database.
        annotations = scamp.annotations.all()
        self.assertEquals(annotations.count(), 0)

    def _attach_dummy_annotation(self, scamp, order):
        Annotation.objects.create(scamp=scamp,
                                  text="Boo %i!" % order,
                                  order=order,
                                  pos_x=10,
                                  pos_y=10,
                                  facing=180)

    def test_annotation_reordering(self):
        scamp = Scamp.objects.get(id=1)
        # At this stage we have one annotation attached
        # due to the fixtures, it's order is 1.
        # We add another 4 in order.
        for i in xrange(2, 6):
            self._attach_dummy_annotation(scamp, i)
        pre_annotations = scamp.annotations.all()
        self.assertEquals(len(pre_annotations), 5)
        # First annotation should be the one from
        # the fixtures as they should come back
        # ordered by 'order'.
        pre_first = pre_annotations[0]
        self.assertEquals(pre_first.text.raw, 'This is a test annotation')
        self.assertEquals(pre_first.order, 1)
        pre_last = pre_annotations[4]
        self.assertEquals(pre_last.text.raw, 'Boo 5!')
        self.assertEquals(pre_last.order, 5)
        # The rest should be ordered as per their return 
        # in the list and should have 'Boo x!' as their text.
        for i, annotation in enumerate(pre_annotations[1:]):
            self.assertEquals(annotation.text.raw, 'Boo %s!' % (i+2))
            self.assertEquals(annotation.order, i+2) # 2 because we've sliced.
        # Now let's start the reordering process.
        reorder_url = reverse('scamp_reorder', args=[scamp.slug])
        reorder_post = {'order': [5, 4, 3, 2, 1, 200]}
        # Not logged in, should 403.
        response = self.client.post(reorder_url, reorder_post)
        self.assertEquals(response.status_code, 403)
        # Now let's login and try again.
        self.client.login(username='admin', password='theteam')
        # Our reorder list has a random ID in it which doesn't
        # exist as an annotation on this scamp, we should 400.
        response = self.client.post(reorder_url, reorder_post)
        self.assertEquals(response.status_code, 400)
        # Remove the crappy ID.
        reorder_post['order'].pop()
        response = self.client.post(reorder_url, reorder_post)
        self.assertEquals(response.status_code, 200)
        # They should have been reorderd now so let's test that.
        post_annotations = scamp.annotations.all()
        # Should still be same amount of annotations.
        self.assertEquals(len(post_annotations), 5)
        post_first = post_annotations[0]
        self.assertEquals(post_first.text.raw, 'Boo 5!')
        self.assertEquals(post_first.order, 1)
        post_last = post_annotations[4]
        self.assertEquals(post_last.text.raw, 'This is a test annotation')
        self.assertEquals(post_last.order, 5)

    def test_scamp_cloning(self):
        """Test that the scamp cloning works
        """
        # Start off with 2 scamps.
        self.assertEquals(Scamp.objects.all().count(), 2)
        scamp = Scamp.objects.get(pk=1)
        clone_url = reverse('scamp_clone', args=[scamp.slug])
        # Scamp shout be cloneable as that is the default.
        self.assertEquals(scamp.is_cloneable, True)
        # Now set it to false and test if we can clone.
        scamp.is_cloneable = False
        scamp.save()
        response = self.client.post(clone_url)
        # Should not be allowed to clone.
        self.assertEquals(response.status_code, 403)
        scamp.is_cloneable = True
        scamp.save()
        response = self.client.post(clone_url)
        # Should now have one more scamp.
        self.assertEquals(Scamp.objects.all().count(), 3)
        # Get that new scamp by latest and check it has the same details.
        new_scamp = Scamp.objects.latest()
        self.assertEquals(scamp.title, new_scamp.title)
        self.assertEquals(scamp.description.raw, scamp.description.raw)
        # Test that the new scamp is cloneable as it should be 
        # by default.
        self.assertEquals(new_scamp.is_cloneable, True)
        # Test that the new scamp has the same amount of tags and annotations
        # as the one it cloned.
        self.assertEquals(scamp.annotations.all().count(), new_scamp.annotations.all().count())
        self.assertEquals(scamp.tags.all().count(), new_scamp.tags.all().count())
