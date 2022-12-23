# Removes the +00:00 at the end of a string if present
# This is a rather simple implementation
def remove_utc_offset_string_from_time_isoformat(strdate):
    return strdate.split("+")[0]