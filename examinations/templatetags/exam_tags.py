from django import template

register = template.Library()

@register.filter
def get_mark_val(existing_marks, args):
    """
    Look up marks from a dict using student_id and subject_id.
    Usage: {{ existing|get_mark_val:"student_id,subject_id" }}
    """
    if not existing_marks:
        return ""
    
    try:
        parts = args.split(',')
        if len(parts) != 2:
            return ""
        
        student_id = int(parts[0])
        subject_id = int(parts[1])
        
        mark_obj = existing_marks.get((student_id, subject_id))
        return mark_obj.marks_obtained if mark_obj else ""
    except (ValueError, TypeError, AttributeError):
        return ""
