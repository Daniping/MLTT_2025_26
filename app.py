from flask import Flask, Response
from ics import Calendar, Event
from datetime import datetime, timedelta

app = Flask(__name__)