import csv
from io import StringIO

import redis
from flask import Flask, render_template, request, jsonify, send_file
from rq import Queue
from walrus import *

from models import push, pull, export
from validate import validate

app = Flask(__name__)

conn = redis.from_url('redis://127.0.0.1:6379')
q = Queue(connection=conn)

wr = Walrus(host='localhost', port=6379, db=0)


def task(email, submission=None):
    record = pull(email)
    if record:
        if record['color'] in ['green', 'red']:
            return record
    response = validate(email)
    created = push(response)
    if submission:
        c = wr.counter(submission + '_completed')
        c.incr()
    return response


def enqueue_emails(emails, submission=None):
    tasks = []
    for email in emails:
        if email:
            t = q.enqueue_call(func='app.task', args=(email, submission), result_ttl=7200, timeout=30)
            tasks.append(t.id)
    return tasks


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


def __process(emails):
    submission = uuid.uuid4().hex
    print(f'[*] New submission: {submission}. Registering...')
    tasks = enqueue_emails(emails=emails, submission=submission)
    l = wr.List(submission + '_tasks')
    try:
        l.extend(tasks)
    except redis.exceptions.ConnectionError:
        for i in tasks:
            l.append(i)
    l = wr.List(submission + '_emails')
    try:
        l.extend(emails)
    except redis.exceptions.ConnectionError:
        for i in emails:
            l.append(i)
    wr.counter(submission + '_completed')
    print(f'[*] Registered submission: {submission}')
    return submission


@app.route('/process', methods=['POST'])
def process():
    f = request.files['file']
    if not f:
        return 'No file'

    stream = StringIO(f.stream.read().decode('UTF8'), newline=None)
    emails = [line[0] for line in csv.reader(stream) if line[0]]
    submission = __process(emails)

    response = {
        'status': 'success',
        'data': {
            'submission_id': submission
        }
    }
    return jsonify(response), 202


@app.route('/status/<submission>', methods=['GET'])
def get_status(submission):
    l = wr.List(submission + '_tasks')
    response = {
        'status': 'success',
        'data': {
            'submission_id': submission,
            'total_tasks': len(l),
            'completed': wr.counter(submission + '_completed').value(),
        }
    }

    deep = request.args.get('deep')
    if deep:
        finished = 0
        failed = 0
        for sub in l:
            job = q.fetch_job(sub.decode('UTF-8'))
            if job.is_finished:
                finished = finished + 1
            elif job.is_failed:
                failed = failed + 1
        response['data']['finished'] = finished
        response['data']['failed'] = failed

    return jsonify(response)


@app.route('/download/<submission>', methods=['GET'])
def download(submission):
    l = wr.List(submission + '_emails')
    records = export(l)

    filename = 'exports/' + submission + '.csv'
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['email', 'syntax', 'mx', 'deliverable', 'color', 'normalized'])
        writer.writerows(records)

    return send_file(filename, as_attachment=True)
