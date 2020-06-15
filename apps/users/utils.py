from apps.utils.constants import SMS_CREDIT

def get_safe_extra_fields(extra_fields):
    not_allowed_fields = [SMS_CREDIT]
    new_extra_fields = {}
    for item in extra_fields.keys():
        if not item in not_allowed_fields:
            new_extra_fields[item] = extra_fields[item]
    return new_extra_fields