from csv import reader, Error
from flask import request, Blueprint
from json import dumps, loads
from geopy import Nominatim, distance
from os import path
from sqlalchemy.exc import NoResultFound
from threading import Thread
from uuid import uuid4
from werkzeug.exceptions import NotFound, BadRequest

from models import Task
from schemas import TaskSchema


app = Blueprint('main', __name__)


def calculate(task: Task, csv_reader):
    geolocator = Nominatim(user_agent='dokka_test')
    data = {
        'points': [],
        'links': [],
    }
    list_of_passed_rows = []
    next(csv_reader)
    for row in csv_reader:
        lat = float(row[1])
        lon = float(row[2])
        data['points'].append({
            'name': row[0],
            'address': geolocator.reverse((lat, lon)).address
        })
        for passed_row in list_of_passed_rows:
            data['links'].append({
                'name': passed_row[0] + row[0],
                'distance': distance.distance((lat, lon), (passed_row[1], passed_row[2])).meters
            })
        list_of_passed_rows.append([row[0], lat, lon])
    task.data = dumps(data, ensure_ascii=False)
    from app import db
    db.session.add(task)
    db.session.commit()


@app.route('/api/calculateDistances', methods=['POST'])
def calculate_distances():
    if 'file' not in request.files:
        raise BadRequest('No file in request')
    content = request.files['file']
    if content.filename == '':
        raise BadRequest('No file in request')
    if path.splitext(content.filename)[1] != '.csv':
        raise BadRequest('Not supported file extension')
    try:
        csv_reader = reader(content.stream.read().decode('utf-8').splitlines())
    except Error:
        raise BadRequest("App can't read the file")
    uuid = str(uuid4())
    task = Task(task_id=uuid)
    from app import db
    db.session.add(task)
    db.session.commit()
    thread = Thread(target=calculate, args=(task, csv_reader))
    thread.start()
    return TaskSchema(exclude=['data']).dump(task)


@app.route('/api/getResult', methods=['GET'])
def get_result():
    task_id = request.args.get('result_id')
    try:
        task = Task.query.get(task_id)
    except NoResultFound:
        raise NotFound('The result_id value not suit to any existing tasks')
    resp = TaskSchema().dump(task)
    return resp
