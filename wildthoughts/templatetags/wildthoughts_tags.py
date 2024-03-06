from django import template
from ..models import UserProfile

register = template.Library()

@register.simple_tag(takes_context=True)
def theme(context):
    request = context['request']
    theme = request.COOKIES.get('theme', 'light')
    return theme

@register.simple_tag(takes_context=True)
def profile_picture(context):
    request = context['request']
    profile = UserProfile.objects.get(user=request.user)
    if profile.picture:
        return profile.picture
    return None