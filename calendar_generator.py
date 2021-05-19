import datetime

text = {
    'upstairs': '<hr>Morning:<br><span class="humanity">Humanity Clean Upstairs</span><br><span class="gex">GEX Re-Prop Upstairs</span><br><br>Evening:<br><span class="gex">GEX Pull Downstairs<span>',
    'downstairs': '<hr>Morning:<br><span class="humanity">Humanity Clean Downstairs</span><br><span class="gex">GEX Re-Prop Downstairs</span><br><br>Evening:<br><span class="gex">GEX Pull Upstairs</span>',
    'tuesday_upstairs': '<hr>Morning:<br><span class="humanity">Humanity Clean Upstairs</span><br><br>Evening:<br><span class="gex">GEX Pull Downstairs<span>',
    'sunday_downstairs': '<hr>Morning:<br><span class="humanity">Humanity Clean Downstairs</span><br><span class="gex">GEX Re-Prop Downstairs</span><br><br>Evening:<br><span class="gex">GEX Pull Upstairs<br>GEX Re-Prop Upstairs</span>',
}

may_data = {'name': 'May', 'begin': (2021, 5, 19), 'end': (2021, 5, 30), 'blanks': 2, 'beginning_upstairs':True}
june_data = {'name': 'June', 'begin': (2021, 5, 31), 'end': (2021, 7, 4), 'blanks': 0, 'beginning_upstairs':True}
july_data = {'name': 'July', 'begin': (2021, 6, 28), 'end': (2021, 7, 31), 'blanks': 0, 'beginning_upstairs':True}

months = (may_data, june_data, july_data)

def output_month_calendar_file(month_data):
    beginning_cleaning_floor_is_upstairs = month_data['beginning_upstairs']
    beginning_date = datetime.date(*month_data['begin'])
    ending_date = datetime.date(*month_data['end'])
    change_date = datetime.date(2021, 6, 14)

    last_cleaning_floor_was_upstairs = False if beginning_cleaning_floor_is_upstairs else True
    num_days = (ending_date + datetime.timedelta(days=1)-beginning_date).days

    head_text = """
    <!doctype html>
    <html>

    <head>
        <meta charset="utf-8">
        <title>""" + month_data['name'] + """ Cleaning Schedule Calendar</title>
        <link rel="stylesheet" href="calendar_styles.css?version=13">
        <link rel="apple-touch-icon" href="/sked/assets/apple-touch-icon.png">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <link rel="icon" type="image/png" sizes="32x32" href="/sked/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/sked/favicon-16x16.png">
        <link rel="manifest" href="/sked/site.webmanifest">
        <link rel="mask-icon" href="/sked/safari-pinned-tab.svg" color="#5bbad5">
        <meta name="msapplication-TileColor" content="#da532c">
        <meta name="theme-color" content="#ffffff">
    </head>

    <body>
    <div class="page-title"><h1>Exhibit Cleaning and Pulling Schedule for """ + month_data['name'] + """<h1></div>
    <table>
    <!--tr><th>Monday</th><th>Tuesday</th><th>Wednesday</th><th>Thursday</th><th>Friday</th><th>Saturday</th><th>Sunday</th></tr>-->
    <!--<td><div class='day-text'></div></td>-->
    """
    if month_data['blanks']:
        head_text = head_text + "<tr>" + ("<td><div class='day-text'></div></td>" * month_data['blanks'])

    foot_text = """
    </table>
    </body>
    </html>
    """

    filename = "_layouts/" + month_data['name'].lower() + ".html"
    with open(filename, 'w') as cleaning_dates_file:
        cleaning_dates_file.write(head_text)
        for day_diff in range(num_days):
            print_day = (beginning_date + datetime.timedelta(days=day_diff))
            weekday = print_day.strftime("%A")
            date_string = print_day.strftime("%A, %B %d")
            if (weekday == "Tuesday" and print_day < change_date) or (weekday == "Monday"):
                line_string = f"<td><div class='dates'>{date_string}</div><hr><div class='day-text'>Closed</div></td>"
            else:
                if last_cleaning_floor_was_upstairs:
                    if weekday == "Sunday" and print_day.strftime("%B") != "May":
                        floor_string = text['sunday_downstairs']
                    else:
                        floor_string = text['downstairs']
                    last_cleaning_floor_was_upstairs = False
                else:
                    if weekday == "Tuesday":
                        floor_string = text['tuesday_upstairs']
                    else:
                        floor_string = text['upstairs']
                    last_cleaning_floor_was_upstairs = True
                last_floor = floor_string
                line_string = f'<td><div class="dates">{date_string}</div><div class="day-text">{floor_string}</div></td>'
            if weekday == "Monday":
                line_string = "<tr>" + line_string
            if weekday == "Sunday":
                line_string = line_string + "</tr>"
            cleaning_dates_file.write(line_string)
        cleaning_dates_file.write(foot_text)

for month in months:
    output_month_calendar_file(month)