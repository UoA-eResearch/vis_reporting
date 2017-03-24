#!/usr/bin/env python
import requests
from icalendar import Calendar
from pprint import pprint
from datetime import datetime
import pytz

data = requests.get('https://calendar.google.com/calendar/ical/lmbm553md5mk5fisj9m2mdj2tk%40group.calendar.google.com/public/basic.ics').content
gcal = Calendar.from_ical(data)
total_hours = 0
assisted_hours = 0
tz = pytz.timezone('Pacific/Auckland')
birth = datetime(2017, 2, 20, tzinfo=tz)
now = datetime.now(tz)
wks_since_birth = (now - birth).days / 7
bookable_hours = wks_since_birth * 5 * 4
for component in gcal.walk():
    if component.name == "VEVENT":
        summary = component.get('summary')
        desc = component.get('description')
        start = component.decoded('dtstart')
        end = component.decoded('dtend')
        duration = end - start
        hours = duration.total_seconds() / 60 / 60
        rrule = component.get('rrule')
        if rrule:
            f = rrule.get('freq')[0]
            if f == 'WEEKLY':
                i = rrule.get('interval', [1])[0]
                wks_since = max((now - start).days / 7, 1)
                hours *= wks_since / i
        total_hours += hours
        if 'nyou045' in desc:
            assisted_hours += hours

print("report generated: {}. total hours used: {}, assisted_hours: {}. total bookable hours since 2017-02-20: {}, utilisation: {}%".format(now, total_hours, assisted_hours, bookable_hours, total_hours/bookable_hours*100))
