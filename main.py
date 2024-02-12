from fastapi import FastAPI
from pydantic import BaseModel
import aiosqlite
import datetime


app = FastAPI()


class EventRequest(BaseModel):
    userid: str
    eventname: str


class ReportRequest(BaseModel):
    lastseconds: int
    userid: str


# init db
async def startup_event():
    async with aiosqlite.connect('events.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS events (
                eventtimestamputc TEXT NOT NULL,
                userid TEXT NOT NULL,
                eventname TEXT NOT NULL
            )
        ''')
        await db.commit()

app.add_event_handler("startup", startup_event)


@app.get("/")
async def welcome():
    return {"message": "Welcome to the Ori's Basic Analytics Server!"}


async def insert_event(userid: str, eventname: str) -> None:
    async with aiosqlite.connect('events.db') as db:
        await db.execute('''
            INSERT INTO events (eventtimestamputc, userid, eventname)
            VALUES (?, ?, ?)
        ''', (datetime.datetime.utcnow().isoformat(), userid, eventname))
        await db.commit()


@app.post("/process_event/")
async def process_event(event_request: EventRequest) -> dict:
    await insert_event(event_request.userid, event_request.eventname)
    return {"message": "Event processed successfully"}


@app.post("/get_reports/")
async def get_reports(request: ReportRequest) -> dict:
    time_threshold = datetime.datetime.utcnow() - datetime.timedelta(seconds=request.lastseconds)

    async with aiosqlite.connect('events.db') as db:
        cursor = await db.execute('''
            SELECT * FROM events WHERE userid = ? AND datetime(eventtimestamputc) > datetime(?)
        ''', (request.userid, time_threshold.isoformat()))
        events = await cursor.fetchall()

    events_list = [{"eventtimestamputc": event[0], "userid": event[1], "eventname": event[2]} for event in events]

    return {"events": events_list}