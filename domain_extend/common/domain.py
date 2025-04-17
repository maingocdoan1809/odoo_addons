from datetime import datetime, timedelta, timezone
from odoo.osv import expression
import pytz
from zoneinfo import ZoneInfo
from dateutil import rrule

date_options = {
    'year': [
        'current_year',
        'previous_year',
        'previous_2_year',
        '3_year_ago',
        'next_year',
        'current_and_previous_year',
        'current_and_next_1_year',
        'current_and_previous_2_year'
    ],
    'fiscal_year': [
        'current_fiscal_year',
        'previous_fiscal_year',
        'previous_2_fiscal_year',
        'next_fiscal_year',
        'current_and_previous_fiscal_year',
        'current_and_previous_2_fiscal_year',
        'current_and_next_fiscal_year'
    ],
    'quarter': [
        'current_quarter',
        'previous_quarter',
        'next_quarter',
        'current_and_previous_quarter',
        'current_and_next_quarter',
        'current_and_next_3_quarter'
    ],
    'month': [
        'this_month',
        'last_month',
        'next_month',
        'current_and_previous_month',
        'current_and_next_month'
    ],
    'week': [
        'this_week',
        'last_week',
        'next_week',
        'current_and_previous_week',
        'current_and_next_week'
    ],
    'day': [
        'today',
        'yesterday',
        'tomorrow',
        'current_and_previous_day',
        'current_and_next_day',
        'last_n_day',
        'next_n_day'
    ]
}

class DateRangeCalculator:
        # ('1', 'Monday'),
        # ('2', 'Tuesday'),
        # ('3', 'Wednesday'),
        # ('4', 'Thursday'),
        # ('5', 'Friday'),
        # ('6', 'Saturday'),
        # ('7', 'Sunday')
    def __init__(self, tz, week_start = 1) -> None:
        self.tz = tz
        self.week_start = week_start - 1

    def convert_domain(self, domain):
        result = []

        for item in domain:
            if expression.is_operator(item):
                result.append(item)

            elif isinstance(item, (list, tuple)) and len(item) == 3:
                field, operator, value = item

                try:
                    try_detect_day = value.split(' ')

                    if len(try_detect_day) == 2 and int(try_detect_day[0]) and try_detect_day[1] in date_options[operator]:
                        value = [try_detect_day[1], int(try_detect_day[0])]
                except:
                    pass
    
                if operator in date_options:

                    if isinstance(value, (list, tuple)) and len(value) == 2:
                        # Value dạng có default_day
                        option, day_count = value
                        if option in date_options[operator]:
                            start, end = self.get_date_range_utc(option, default_day=day_count)
                            if start and end:
                                result.extend(['&', (field, '>=', start), (field, '<=', end)])
                                continue

                    elif isinstance(value, str) and value in date_options[operator]:
                        start, end = self.get_date_range_utc(value)
                        if start and end:
                            result.extend(['&', (field, '>=', start), (field, '<=', end)])
                            continue

                result.append(item if isinstance(item, list) else list(item))

            else:
                result.append(item)

        return result

    def get_date_range_utc(self, option, default_day=1):
        date_range = self.get_date_range(option, default_day)
        [start, end] = date_range
        if start:
            start = start.astimezone(pytz.UTC)
        if end:
            end = end.astimezone(pytz.UTC)
        return [start, end]
    def get_date_range(self, option, default_day=1):
        now = datetime.now(tz=pytz.timezone(self.tz))
        year = now.year

        if option == 'current_year':
            return [datetime(year, 1, 1, tzinfo=ZoneInfo(self.tz)),
                    datetime(year, 12, 31, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))]
        elif option == 'previous_year':
            return [datetime(year - 1, 1, 1, tzinfo=ZoneInfo(self.tz)),
                    datetime(year - 1, 12, 31, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))]
        elif option == 'previous_2_year':
            return [datetime(year - 2, 1, 1, tzinfo=ZoneInfo(self.tz)),
                    datetime(year - 2, 12, 31, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))]
        elif option == '3_year_ago':
            return [datetime(year - 3, 1, 1),
                    datetime(year - 3, 12, 31, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))]
        elif option == 'next_year':
            return [datetime(year + 1, 1, 1, tzinfo=ZoneInfo(self.tz)),
                    datetime(year + 1, 12, 31, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))]
        elif option == 'current_and_previous_year':
            return [datetime(year - 1, 1, 1, tzinfo=ZoneInfo(self.tz)),
                    datetime(year, 12, 31, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))]
        elif option == 'current_and_next_1_year':
            return [datetime(year, 1, 1, tzinfo=ZoneInfo(self.tz)),
                    datetime(year + 1, 12, 31, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))]
        elif option == 'current_and_previous_2_year':
            return [datetime(year - 2, 1, 1, tzinfo=ZoneInfo(self.tz)),
                    datetime(year, 12, 31, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))]

        elif option == 'current_fiscal_year':
            return self._get_fiscal_year_range(year)
        elif option == 'previous_fiscal_year':
            return self._get_fiscal_year_range(year - 1)
        elif option == 'previous_2_fiscal_year':
            return self._get_fiscal_year_range(year - 2)
        elif option == 'next_fiscal_year':
            return self._get_fiscal_year_range(year + 1)
        elif option == 'current_and_previous_fiscal_year':
            return [self._get_fiscal_year_range(year - 1)[0], self._get_fiscal_year_range(year)[1]]
        elif option == 'current_and_previous_2_fiscal_year':
            return [self._get_fiscal_year_range(year - 2)[0], self._get_fiscal_year_range(year)[1]]
        elif option == 'current_and_next_fiscal_year':
            return [self._get_fiscal_year_range(year)[0], self._get_fiscal_year_range(year + 1)[1]]

        elif option == 'current_quarter':
            return self._get_quarter_range(now)
        elif option == 'previous_quarter':
            return self._get_quarter_range(self._add_months(now, -3))
        elif option == 'next_quarter':
            return self._get_quarter_range(self._add_months(now, 3))
        elif option == 'current_and_previous_quarter':
            return [self._get_quarter_range(self._add_months(now, -3))[0], self._get_quarter_range(now)[1]]
        elif option == 'current_and_next_quarter':
            return [self._get_quarter_range(now)[0], self._get_quarter_range(self._add_months(now, 3))[1]]
        elif option == 'current_and_next_3_quarter':
            return [self._get_quarter_range(now)[0], self._get_quarter_range(self._add_months(now, 9))[1]]

        elif option == 'this_month':
            return [datetime(year, now.month, 1, tzinfo=ZoneInfo(self.tz)),
                    self._end_of_month(now.year, now.month)]
        elif option == 'last_month':
            last_month = self._add_months(now, -1)
            return [datetime(last_month.year, last_month.month, 1, tzinfo=ZoneInfo(self.tz)),
                    self._end_of_month(last_month.year, last_month.month)]
        elif option == 'next_month':
            next_month = self._add_months(now, 1)
            return [datetime(next_month.year, next_month.month, 1, tzinfo=ZoneInfo(self.tz)),
                    self._end_of_month(next_month.year, next_month.month)]
        elif option == 'current_and_previous_month':
            last_month = self._add_months(now, -1)
            return [datetime(last_month.year, last_month.month, 1, tzinfo=ZoneInfo(self.tz)),
                    self._end_of_month(now.year, now.month)]
        elif option == 'current_and_next_month':
            next_month = self._add_months(now, 1)
            return [datetime(year, now.month, 1, tzinfo=ZoneInfo(self.tz)),
                    self._end_of_month(next_month.year, next_month.month)]

        elif option == 'this_week':
            return self._get_week_range(now)
        elif option == 'last_week':
            return self._get_week_range(self._add_days(now, -7))
        elif option == 'next_week':
            return self._get_week_range(self._add_days(now, 7))
        elif option == 'current_and_previous_week':
            return [self._get_week_range(self._add_days(now, -7))[0], self._get_week_range(now)[1]]
        elif option == 'current_and_next_week':
            return [self._get_week_range(now)[0], self._get_week_range(self._add_days(now, 7))[1]]

        elif option == 'today':
            return [self._start_of_day(now), self._end_of_day(now)]
        elif option == 'yesterday':
            y = self._add_days(now, -1)
            return [self._start_of_day(y), self._end_of_day(y)]
        elif option == 'tomorrow':
            t = self._add_days(now, 1)
            return [self._start_of_day(t), self._end_of_day(t)]
        elif option == 'current_and_previous_day':
            y = self._add_days(now, -1)
            return [self._start_of_day(y), self._end_of_day(now)]
        elif option == 'current_and_next_day':
            t = self._add_days(now, 1)
            return [self._start_of_day(now), self._end_of_day(t)]

        elif option == 'last_n_day':
            target = self._add_days(now, -default_day)
            return [self._start_of_day(target), self._end_of_day(target)]
        elif option == 'next_n_day':
            target = self._add_days(now, default_day)
            return [self._start_of_day(target), self._end_of_day(target)]
        else:
            return [None, None]

    def _get_fiscal_year_range(self, year):
        return [
            datetime(year, 4, 1, tzinfo=ZoneInfo(self.tz)),
            datetime(year + 1, 3, 31, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))
        ]

    def _get_quarter_range(self, date):
        month = date.month
        start_month = ((month - 1) // 3) * 3 + 1
        start = datetime(date.year, start_month, 1, tzinfo=ZoneInfo(self.tz))
        end = self._end_of_month(date.year if start_month + 2 <= 12 else date.year, start_month + 2)
        return [start, end]

    def _get_week_range(self, date):
        delta = (7 - self.week_start) % 7
        day = date.weekday() + delta if date.weekday() != (7 - delta) else (date.weekday() - self.week_start)
        start = datetime(date.year, date.month, date.day, tzinfo=ZoneInfo(self.tz)) - timedelta(days=day)
        start = self._start_of_day(start)
        end = self._end_of_day(start + timedelta(days=6))
        return [start, end]

    def _add_days(self, date, days):
        return date + timedelta(days=days)

    def _add_months(self, date, months):
        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1
        day = min(date.day, (datetime(year, month + 1, 1, tzinfo=ZoneInfo(self.tz)) - timedelta(days=1)).day)
        return datetime(year, month, day, date.hour, date.minute, date.second, date.microsecond, tzinfo=ZoneInfo(self.tz))

    def _start_of_day(self, date):
        return datetime(date.year, date.month, date.day, tzinfo=ZoneInfo(self.tz))

    def _end_of_day(self, date):
        return datetime(date.year, date.month, date.day, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))

    def _end_of_month(self, year, month):
        if month == 12:
            return datetime(year, month, 31, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))
        else:
            last_day = datetime(year, month + 1, 1, tzinfo=ZoneInfo(self.tz)) - timedelta(days=1)
            return datetime(last_day.year, last_day.month, last_day.day, 23, 59, 59, 999000, tzinfo=ZoneInfo(self.tz))
    def _year_start(self, year):
        return datetime(year, 1, 1, tzinfo=ZoneInfo(self.tz))

    def _year_end(self, year):
        return datetime(year, 12, 31, 23, 59, 59, 999999, tzinfo=ZoneInfo(self.tz))

    def _year_range(self, year):
        return (self._year_start(year), self._year_end(year))

    def _fiscal_start(self, year):
        return datetime(year, 4, 1, tzinfo=ZoneInfo(self.tz))

    def _fiscal_end(self, year):
        return datetime(year + 1, 3, 31, 23, 59, 59, 999999, tzinfo=ZoneInfo(self.tz))

    def _fiscal_year_range(self, year):
        return (self._fiscal_start(year), self._fiscal_end(year))

    def _day_range(self, date):
        return (self._start_of_day(date), self._end_of_day(date))

    def _range(self, start, end):
        return (start, end)
