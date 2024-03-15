from django import template
from ..models import UserProfile

register = template.Library()

UPVOTE_CLASS = "btn btn-outline-danger border-0";
DOWNVOTE_CLASS = "btn btn-outline-primary border-0";
NORMAL_CLASS = "btn btn-outline-secondary border-0";

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

@register.simple_tag(takes_context=True)
def profile(context):
    request = context['request']
    try:
        profile = UserProfile.objects.get(user=request.user)
        return profile
    except:
        return None
    
@register.inclusion_tag('wildthoughts/widget/vote_widget.html')
def render_vote(category, instance, profile):
    upvote_class = NORMAL_CLASS
    upvote_status = 'upvote'
    downvote_class = NORMAL_CLASS
    downvote_status = 'downvote'
    
    if profile:
        if instance.upvoted_by.filter(id=profile.id).exists():
            upvote_class = UPVOTE_CLASS
            upvote_status = 'upvoted'
            downvote_class = NORMAL_CLASS
            downvote_status = 'downvote'
        elif instance.downvoted_by.filter(id=profile.id).exists():
            upvote_class = NORMAL_CLASS
            upvote_status = 'upvote'
            downvote_class = DOWNVOTE_CLASS
            downvote_status = 'downvoted'

    context_dict = {
        'category': category,
        'upvote_class': upvote_class,
        'downvote_class': downvote_class,
        'upvote_status': upvote_status,
        'downvote_status': downvote_status,
        'id': instance.id,
        'votes':  instance.votes
    }

    return context_dict