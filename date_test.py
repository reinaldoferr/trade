import pytz#; pytz.all_timezones 
import datetime as dt

# a timestamp I'd like to convert
my_timestamp = dt.datetime.now()

# create both timezone objects
old_timezone = pytz.timezone("America/Buenos_Aires")
new_timezone = pytz.timezone("Europe/London")
print(old_timezone)
print(new_timezone)

# two-step process
localized_timestamp = old_timezone.localize(my_timestamp)
new_timezone_timestamp = localized_timestamp.astimezone(new_timezone)

print(localized_timestamp)
print(new_timezone_timestamp)

# or alternatively, as an one-liner
new_timezone_timestamp = old_timezone.localize(my_timestamp).astimezone(new_timezone) 