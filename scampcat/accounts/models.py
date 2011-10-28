from django.db import models

from social_auth.signals import socialauth_registered


class UserProfile(models.Model):
    """``UserProfile`` for storing the ``User`` twitter details"""
    user = models.OneToOneField('auth.User')
    avatar_url = models.URLField(verify_exists=False, blank=True)
    avatar = models.ImageField(upload_to="profile", blank=True)
    twitter_id = models.CharField(blank=True, max_length=255)

    def __unicode__(self):
        return 'Profile for %s (%s)' % (self.user, self.twitter_id)


def profile_creator(sender, user, response, details, **kwargs):
    """``response`` for ``twitter`` contains the followind data
    {u'follow_request_sent': False,
    u'profile_use_background_image': True, 
    u'profile_background_image_url_https': u'https://si0.twimg.com/images/themes/theme1/bg.png', 
    u'description': None, 
    u'verified': False, 
    u'profile_image_url_https': u'https://si0.twimg.com/sticky/default_profile_images/default_profile_2_normal.png',
    u'profile_sidebar_fill_color': u'DDEEF6', 
    u'id': 330856703, 
    u'profile_text_color': u'333333', 
    u'followers_count': 0, 
    u'protected': False, 
    u'id_str': u'330856703', 
    u'default_profile_image': True, 
    u'listed_count': 0, 
    u'utc_offset': None, 
    u'statuses_count': 0, 
    u'profile_background_color': u'C0DEED', 
    u'friends_count': 0, 
    u'location': None, 
    u'profile_link_color': u'0084B4', 
    u'profile_image_url': u'http://a1.twimg.com/sticky/default_profile_images/default_profile_2_normal.png', 
    u'following': False, 
    u'show_all_inline_media': False, 
    u'geo_enabled': False, 
    u'profile_background_image_url': u'http://a0.twimg.com/images/themes/theme1/bg.png', 
    u'name': u'Scamp Cat', 
    u'lang': u'en', 
    u'profile_background_tile': False, 
    u'favourites_count': 0, 
    u'screen_name': u'ScampCatApp', 
    u'notifications': False, 
    u'url': None, 
    u'created_at': u'Thu Jul 07 08:02:46 +0000 2011', 
    u'contributors_enabled': False, 
    u'time_zone': None, 
    'access_token': 'oauth_token_secret=Kqtl23h3KZuBEcvg4EGReVxJLtqB0fAoZpO37QzeE&oauth_token=330856703-cWwysmOmdlQG6EgtnuRWUvmKcmJpeENnrFzh1sVQ', 
    u'profile_sidebar_border_color': u'C0DEED', 
    u'default_profile': True, 
    u'is_translator': False}
    """
    data = {'user': user,
            'avatar_url': response['profile_image_url'],
            'twitter_id': response['screen_name']}
    UserProfile.objects.create(**data)
    return False

socialauth_registered.connect(profile_creator, sender=None)