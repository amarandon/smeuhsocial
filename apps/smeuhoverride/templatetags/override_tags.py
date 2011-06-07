#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django import template
from django.utils.safestring import mark_safe
from microblogging.templatetags.microblogging_tags import (
        render_tweet_text as _render_tweet_text,
        user_ref_re,
        make_user_link,
        )

register = template.Library()

@register.simple_tag
def render_tweet_text(tweet):
    """
    Override render_tweet_text from microblogging to make URLs clickable
    """
    text = _render_tweet_text(tweet)
    text = template.defaultfilters.urlize(text)
    return text

@register.inclusion_tag("_user_link.html")
def profile_link(member):
    return {'member': member}

@register.filter
def profilize(text):
    """
    Replace @username by a link to the profile page
    """
    text = user_ref_re.sub(make_user_link, text)
    return mark_safe(text)
