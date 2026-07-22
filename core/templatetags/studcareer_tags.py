from django import template
from django.utils import timezone

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context["request"].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()


@register.filter
def duration_from(value):
    if not value:
        return ""
    days = (timezone.now() - value).days
    if days == 0:
        return "Сегодня"
    if days == 1:
        return "Вчера"
    if days < 7:
        return f"{days} дн. назад"
    if days < 30:
        return f"{days // 7} нед. назад"
    if days < 365:
        return f"{days // 30} мес. назад"
    return f"{days // 365} г. назад"


@register.filter
def status_color(value):
    colors = {
        "sent": "bg-amber-50 text-amber-600",
        "viewed": "bg-blue-50 text-blue-600",
        "invited": "bg-emerald-50 text-emerald-600",
        "rejected": "bg-rose-50 text-rose-600",
    }
    return colors.get(value, "bg-slate-50 text-slate-600")


@register.filter
def work_type_label(value):
    labels = {
        "remote": "Удалённо",
        "office": "В офисе",
        "hybrid": "Гибрид",
    }
    return labels.get(value, value)
