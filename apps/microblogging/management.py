from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from django.apps import apps

try:
    from notification import models as notification
    notification_appconfig = apps.get_app_config('notification')
    
    def create_notice_types(*args, **kwargs):
        notification.create_notice_type("tweet_follow", _("New Tweet Follower"), _("someone has started following your tweets"))
        notification.create_notice_type("tweet_reply_received", _("New Tweet Reply"), _("someone sent a tweet reply to you"))
    
    signals.post_migrate.connect(create_notice_types, sender=notification_appconfig)
except ImportError:
    print "Skipping creation of NoticeTypes as notification app not found"
