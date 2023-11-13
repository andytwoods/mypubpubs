from arrow import arrow, get
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now


def date_formats():
    ''' based on Arrow string formats at http://crsmithdev.com/arrow/#tokens '''
    date_formats = [('Tuesday, 12 January, 2016', 'dddd, D MMMM, YYYY'),
                    ('Tuesday, 12 January', 'dddd, D MMMM'),
                    ('14 Jan 2016', 'D MMM YYYY'),
                    ('12-1-2016', 'DD-MM-YYYY')]
    return date_formats


def form(request):
    if request.POST:
        return form_post(request)

    current_year = now().year
    years = [str(y) for y in range(current_year, current_year + 10)]
    months = [x for x in locale().month_names if len(x) > 0]
    ddays = [str(d) for d in range(1, 32)]
    formats = [t[0] for t in date_formats()]
    context = {
        'years': years,
        'months': months,
        'ddays': ddays,
        'formats':   formats,
    }
    return render(request, 'academic_scheduler/form.html', context=context)


def locale():
    return arrow.locales.get_locale('en_us')


def form_post(request):
    year = int(request.POST.get('year'))
    start_month = locale().month_number(request.POST.get('start-month').lower())
    start_day = int(request.POST.get('start-day'))
    last_month = locale().month_number(request.POST.get('last-month').lower())
    last_day = int(request.POST.get('last-day'))
    weekdays = request.POST.getlist('days')
    date_fmt = [b for (a, b) in date_formats() if a == request.POST.get('format')][0]
    week_numbers = request.POST.get('week_numbers', 'No') == 'Yes'

    try:
        start_date = [get(year, start_month, start_day)]
    except:
        return "The starting date you specified does not exist."

    try:
        last_date = [get(year, last_month, last_day)]
    except:
        return "The ending date you specified does not exist."

    possible_classes, no_classes = sorted_classes(weekdays, start_date, last_date, no_classes=[])
    course = schedule(possible_classes, no_classes, show_no=True, fmt=date_fmt, week_numbers=week_numbers)

    return HttpResponse('<br/>'.join(course))


def sorted_classes(weekdays, first_day, last_day, no_classes):
    ''' Take class meetings as list of day names, return lists of Arrow objects '''
    semester = range_of_days(first_day[0], last_day[0])
    possible_classes = [d for d in semester if locale().day_name(d.isoweekday()) in weekdays]
    return possible_classes, no_classes


def schedule(possible_classes, no_classes, show_no=None, fmt=None, week_numbers=True):
    ''' Take lists of Arrow objects, return list of course meetings as strings '''
    course = []
    date_format = fmt if fmt else 'dddd, MMMM D, YYYY'

    locale()

    start_week = -1
    for d in possible_classes:
        if week_numbers:
            if start_week < 0:
                start_week = d.isocalendar().week - 1
            extra_week_info = 'week ' + str(d.isocalendar().week - start_week) + ' — '
        else:
            extra_week_info = ''
        if d not in no_classes:
            course.append(extra_week_info + d.format(date_format))
        elif show_no:
            course.append(extra_week_info + d.format(date_format) + ' - NO CLASS')
    return course


def range_of_days(start, end):
    return arrow.Arrow.range('day', start, end)
