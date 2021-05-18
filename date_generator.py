import datetime

text = {
    'upstairs': 'Morning: Clean Upstairs, Re-Prop Upstairs, Evening: Pull Downstairs',
    'downstairs': 'Morning: Clean Downstairs, Re-Prop Downstairs, Evening: Pull Upstairs',
}

beginning_cleaning_floor_is_upstairs = True
beginning_date = datetime.date(2021, 5, 19)
ending_date = datetime.date(2021, 8, 1)
change_date = datetime.date(2021, 5, 20)

last_cleaning_floor_was_upstairs = False if beginning_cleaning_floor_is_upstairs else True
num_days = (ending_date + datetime.timedelta(days=1)-beginning_date).days

print(num_days)

with open('dates.csv', 'w') as cleaning_dates_file:
    for day_diff in range(num_days):
        print_day = (beginning_date + datetime.timedelta(days=day_diff))
        date_string = print_day.strftime("%B %d, %A")
        if print_day < change_date:
            if (print_day.strftime("%A") == "Monday" or print_day.strftime("%A") == "Tuesday"):
                continue
        else:
            if (print_day.strftime("%A") == "Monday"):
                continue
        if last_cleaning_floor_was_upstairs:
            floor_string = text['downstairs']
            last_cleaning_floor_was_upstairs = False
        else:
            floor_string = text['upstairs']
            last_cleaning_floor_was_upstairs = True
        last_floor = floor_string
        line_string = f'{date_string}, {floor_string}\n' # Enclose commas in double quotes to escape
        cleaning_dates_file.write(line_string)