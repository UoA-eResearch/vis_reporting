#!/usr/bin/env python
import requests
from icalendar import Calendar
from pprint import pprint
from datetime import datetime, date
import pytz

BOOKABLE_HOURS_PER_DAY = 4

data = requests.get('https://calendar.google.com/calendar/ical/lmbm553md5mk5fisj9m2mdj2tk%40group.calendar.google.com/public/basic.ics').content
gcal = Calendar.from_ical(data)
total_hours = 0
assisted_hours = 0
per_year = {
  2017: 0,
  2018: 0,
  2019: 0
}
tz = pytz.timezone('Pacific/Auckland')
birth = datetime(2017, 2, 20, tzinfo=tz)
now = datetime.now(tz)
wks_since_birth = (now - birth).days / 7
total_bookable_hours = wks_since_birth * 5 * BOOKABLE_HOURS_PER_DAY
for component in gcal.walk():
    if component.name == "VEVENT":
        summary = component.get('summary')
        desc = component.get('description')
        start = component.decoded('dtstart')
        if type(start) is datetime and start > now:
          continue
        elif type(start) is date and start > now.date():
          continue
        try:
          end = component.decoded('dtend')
        except KeyError:
          print("{} has no end!".format(summary))
          continue
        duration = end - start
        hours = duration.total_seconds() / 60 / 60
        if hours > 24:
          # long booking - likely an offsite gear loan
          #print("ignoring {}".format(summary))
          continue
        rrule = component.get('rrule')
        if rrule:
            f = rrule.get('freq')[0]
            if f == 'WEEKLY':
                i = rrule.get('interval', [1])[0]
                if "COUNT" in rrule:
                  hours *= rrule["COUNT"][0]
                  per_year[start.year] += hours
                elif "UNTIL" in rrule:
                  hours *= (rrule["UNTIL"][0] - start).days / 7
                  per_year[start.year] += hours
                else:
                  # indefinite
                  for year in per_year:
                      start_of_year = datetime(year, 1, 1, tzinfo=tz)
                      end_of_year = datetime(year, 12, 31, tzinfo=tz)
                      if year == now.year:
                        if start < start_of_year:
                          per_year[year] += hours * ((now - start_of_year).days / 7)
                        else:
                          per_year[year] += hours * ((now - start).days / 7)
                      elif year == start.year:
                        per_year[year] += hours * ((end_of_year - start).days / 7)
                      else:
                        per_year[year] += hours * 52
                  wks_since = max((now - start).days / 7, 1)
                  hours *= wks_since / i
        else:
            per_year[start.year] += hours
        if start.year == 2019:
          print("{},{}".format(hours, summary.encode("ascii", "ignore")))
        total_hours += hours
        if 'nyou045' in desc:
            assisted_hours += hours

for year, hours in per_year.items():
  print(year)
  if year == 2017:
    delta = datetime(2017, 12, 31, tzinfo=tz) - birth
    weeks = delta.days / 7
  elif year == now.year:
    delta = now - datetime(now.year, 1, 1, tzinfo=tz)
    weeks = delta.days / 7
  else:
    weeks = 52
  bookable_hours = weeks * 5 * BOOKABLE_HOURS_PER_DAY
  print("hours: {}, bookable hours: {}, utilisation: {}%".format(hours, bookable_hours, hours/bookable_hours*100))
print("report generated: {}. total hours used: {}, assisted_hours: {}. total bookable hours since 2017-02-20: {}, utilisation: {}%".format(
  now, total_hours, assisted_hours, total_bookable_hours, total_hours/total_bookable_hours*100))
