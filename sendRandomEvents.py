import random
import string
from joblib import Parallel, delayed
import requests


EVENT_URL = "http://20.217.133.180/process_event/"


def random_user_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))


def random_event_name():
    events = ['login', 'logout', 'click', 'view', 'signup']
    return random.choice(events)


def send_event():
    data = {
        "userid": random_user_id(),
        "eventname": random_event_name()
    }
    response = requests.post(EVENT_URL, json=data)
    if response.status_code == 200:
        print(f"Event sent: {data}")
    else:
        print(f"Failed to send event: {response.text}")


def send_events_in_parallel(num_events, num_jobs=-1):
    # num_jobs=-1 means using all available cores
    Parallel(n_jobs=num_jobs)(delayed(send_event)() for _ in range(num_events))


if __name__ == "__main__":
    send_events_in_parallel(1000)
