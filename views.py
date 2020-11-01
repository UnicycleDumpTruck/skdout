import datetime

from tablib import Dataset
from skd.resources import TaskResource

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

import pandas as pd

from .models import Task

from bakery.views import BuildableTemplateView


def time_to_date(input_time):
    return datetime.datetime.combine(datetime.date(2020, 1, 1), input_time)


def prep_df(day_of_week):
    task_list = Task.objects.filter(weekday=day_of_week.lower().capitalize())
    no_virex = task_list.exclude(task_text="Virex Spray Everything")
    q = no_virex.values(
        "location",
        "start_time",
        "end_time",
        "task_text",
        "weekday",
    )

    df = pd.DataFrame.from_records(q)
    df["start_date"] = df.start_time.apply(time_to_date)
    df["end_date"] = df.end_time.apply(time_to_date)
    df["start_string"] = df.start_time.apply(lambda x: x.strftime("%H:%M"))
    df["end_string"] = df.end_time.apply(lambda x: x.strftime("%H:%M"))
    df["caption"] = (
        df["start_string"]
        + " to "
        + df["end_string"]
        + "<br>"
        + df["location"]
        + "<br>"
        + df["task_text"].replace("Disinfect & Prop Swap",
                                  "Disinfect<br>& Prop Swap")
    )
    df["class"] = df.task_text.apply(lambda r: task_classes.get(r, "unknown"))
    df["icons"] = df.task_text.apply(lambda r: icons.get(r))
    return df


def simple_upload(request):
    if request.method == "POST":
        person_resource = TaskResource()
        dataset = Dataset()
        new_persons = request.FILES["myfile"]

        imported_data = dataset.load(new_persons.read())
        result = person_resource.import_data(
            dataset, dry_run=True
        )  # Test the data import

        if not result.has_errors():
            person_resource.import_data(
                dataset, dry_run=False)  # Actually import now

    return render(request, "core/simple_upload.html")


def per_delta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta
    # usage: for result in per_delta(datetime.datetime.now(), datetime.datetime.now().replace(hour=19))


def list_of_times(start, end, delta):
    return list(result.strftime("%H:%M") for result in per_delta(start, end, delta))


def day_of_times():
    return list_of_times(
        datetime.datetime(2020, 1, 1, 0, 0, 0, 0),
        datetime.datetime(2020, 1, 1, 23, 59, 59, 0),
        datetime.timedelta(minutes=15),
    )


task_rows = {
    "Learn & Play": 2,
    "Closed to Public": 2,
    "Disinfect & Prop Swap": 3,
    "Wipe down": 4,
    "Prop Swap": 3,
    "Prop Swap Only": 3,
}


task_classes = {
    "Learn & Play": "learn_and_play",
    "Closed to Public": "closed_to_public",
    "Disinfect & Prop Swap": "spray_and_swap",
    "Wipe down": "wipe_down",
    "Prop Swap": "prop_swap",
    "Prop Swap Only": "prop_swap",
}


icons = {
    "Learn & Play": ("close.png", "learn.png"),
    "Closed to Public": ("close.png", "learn.png"),
    "Disinfect & Prop Swap": (
        "close.png",
        "swap.png",
        "spray.png",
    ),
    "Wipe down": (
        "open.png",
        "wipe.png",
    ),
    "Prop Swap": (
        "open.png",
        "swap.png",
    ),
    "Prop Swap Only": (
        "open.png",
        "swap.png",
    ),
}

weekdays = ["Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Weekend", "Weekend"]


def grid(request):
    template = loader.get_template("polls/grid.html")
    time_list = list_of_times(
        datetime.datetime(2020, 1, 1, 8, 45, 0, 0),
        datetime.datetime(2020, 1, 1, 16, 0, 0, 0),
        datetime.timedelta(minutes=15),
    )
    wed_df = prep_df("Wednesday")
    wed_df["start_col"] = wed_df.start_date.apply(
        lambda x: time_list.index(x.strftime("%H:%M")) + 1
    )
    wed_df["end_col"] = wed_df.end_date.apply(
        lambda x: time_list.index(x.strftime("%H:%M")) + 1
    )
    wed_df["row"] = wed_df.task_text.apply(lambda r: task_rows.get(r, 6))

    wed_events = wed_df.to_dict("index").values()

    context = {
        "num_columns": len(time_list),
        "col_width": (100 / (len(time_list))),
        "wed_events": wed_events,
        "time_list": enumerate(time_list, 1),
    }
    return HttpResponse(template.render(context, request))


def vgrid(request, weekday):
    template = loader.get_template("polls/vgrid.html")
    if weekday.lower() == "today":
        weekday = weekdays[datetime.datetime.today().weekday()]
    df = prep_df(weekday)

    # Remove Members Only events
    df = df[~df['task_text'].str.contains("Members Only")]
    df = df[~df['task_text'].str.contains("Activity Room Play")]
    df = df[~df['task_text'].str.contains("Camp staff clean")]

    time_list = list_of_times(
        datetime.datetime.combine(datetime.date(
            2020, 1, 1), min(df['start_time'])),  # Earliest time in df
        datetime.datetime.combine(datetime.date(
            2020, 1, 1), max(df['end_time'])) + datetime.timedelta(minutes=15),  # Latest time in df
        datetime.timedelta(minutes=15),  # Interval of time list
    )
    hour_rows = [
        (index, time) for (index, time) in enumerate(time_list, 1) if time[2:] == ":00"
    ]

    df["start_row"] = df.start_date.apply(
        lambda x: time_list.index(x.strftime("%H:%M")) + 1
    )
    df["end_row"] = df.end_date.apply(
        lambda x: time_list.index(x.strftime("%H:%M")) + 1
    )
    df["row"] = df.task_text.apply(lambda r: task_rows.get(r, 6))
    events = df.to_dict("index").values()

    context = {
        "num_rows": len(time_list),
        "weekday": weekday.lower().capitalize(),
        "events": events,
        "time_list": enumerate(time_list, 1),
        "hour_rows": hour_rows,
    }
    return HttpResponse(template.render(context, request))


class VerticalGridView(BuildableTemplateView):
    build_path = "test.html"
    template_name = "vgrid.html"

    def get(self, request, weekday="Friday"):
        # def vgrid(request, weekday):
        template = loader.get_template("polls/vgrid.html")
        if weekday.lower() == "today":
            weekday = weekdays[datetime.datetime.today().weekday()]
        df = prep_df(weekday)

        # Remove Members Only events
        df = df[~df['task_text'].str.contains("Members Only")]
        df = df[~df['task_text'].str.contains("Activity Room Play")]
        df = df[~df['task_text'].str.contains("Camp staff clean")]

        time_list = list_of_times(
            datetime.datetime.combine(datetime.date(
                2020, 1, 1), min(df['start_time'])),  # Earliest time in df
            datetime.datetime.combine(datetime.date(
                2020, 1, 1), max(df['end_time'])) + datetime.timedelta(minutes=15),  # Latest time in df
            datetime.timedelta(minutes=15),  # Interval of time list
        )
        hour_rows = [
            (index, time) for (index, time) in enumerate(time_list, 1) if time[2:] == ":00"
        ]

        df["start_row"] = df.start_date.apply(
            lambda x: time_list.index(x.strftime("%H:%M")) + 1
        )
        df["end_row"] = df.end_date.apply(
            lambda x: time_list.index(x.strftime("%H:%M")) + 1
        )
        df["row"] = df.task_text.apply(lambda r: task_rows.get(r, 6))
        events = df.to_dict("index").values()

        context = {
            "num_rows": len(time_list),
            "weekday": weekday.lower().capitalize(),
            "events": events,
            "time_list": enumerate(time_list, 1),
            "hour_rows": hour_rows,
        }
        return HttpResponse(template.render(context, request))
