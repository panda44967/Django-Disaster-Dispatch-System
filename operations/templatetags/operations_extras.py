from django import template

register = template.Library()


@register.filter
def active_label(value):
    """Display 處理中 / 已結案 for boolean is_active."""
    if value is True:
        return "處理中"
    return "已結案"


@register.simple_tag
def page_heading(main, sub=None):
    """Template tag example for exam requirement."""
    if sub:
        return f"{main} — {sub}"
    return main
