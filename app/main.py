from fastapi import FastAPI, HTTPException
import os
import pandas as pd
import datetime as dt
from fastapi.responses import Response
from icalendar import Calendar, Event

app = FastAPI()


@app.get("/list/schedules")
def list_options():
    """
    Lists the available training plan options
    """
    return os.listdir("schedules")


@app.get("/items/generate_ical")
def generate_ical(schedule_name: str, start_date: dt.date):
    """
    Generates an ical for a training schedule with a given starting date
    """
    if not schedule_name in os.listdir("schedules"):
        return HTTPException(status_code=422, detail="Please choose an option amongst the available schedule options")
    full_schedule_path = f"schedules/{schedule_name}"
    # Create a table of events based on schedule
    schedule = pd.read_csv(full_schedule_path, header=None, skiprows=1, names=["description"]).reset_index()
    with open(full_schedule_path) as f:
        schedule.about = f.readline()
    schedule['date'] = schedule['index'].apply(lambda x: start_date + dt.timedelta(days=x))
    # Load events into Calendar
    cal = Calendar()
    cal.add('prodid', '-//Fast Walking//Running Training Planner//EN')
    cal.add('version', '2.1')
    for index, row in schedule.iterrows():
        cal.add_component(Event({"summary": row.description, "DTSTART;VALUE=DATE": row.date.strftime("%Y%m%d"),
                                 "DTEND;VALUE=DATE": (row.date + dt.timedelta(days=1)).strftime("%Y%m%d"),
                                 "description": f"For details, click here {schedule.about}"}))

    return Response(cal.to_ical(), media_type="text/calendar")
