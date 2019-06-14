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


def fetch_record(email):
    record = pull(email)
    if record:
        if email['color'] in ['green', 'red']:
            return record
    response = validate(email)
    created = push(response)
    return response


def enqueue_emails(emails):
    tasks = []
    for email in emails:
        if email:
            t = q.enqueue_call(func='batch.task', args=(email,), result_ttl=7200, timeout=30)
            tasks.append(t.id)
    return tasks


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    f = request.files['file']
    if not f:
        return 'No file'

    stream = StringIO(f.stream.read().decode('UTF8'), newline=None)
    emails = [line[0] for line in csv.reader(stream)]
    tasks = enqueue_emails(emails=emails)
    submission = uuid.uuid4().hex
    print(f'[*] New submission: {submission}')
    l = wr.List(submission+'_tasks')
    l.extend(tasks)
    l = wr.List(submission+'_emails')
    l.extend(emails)

    response = {
        'status': 'success',
        'data': {
            'submission_id': submission
        }
    }
    return jsonify(response), 202


@app.route('/status/<submission>', methods=['GET'])
def get_status(submission):
    l = wr.List(submission+'_tasks')
    count = 0
    completed = True

    for tid in l:
        if q.fetch_job(str(tid)):
            count = count + 1
        else:
            completed = False

    response = {
        'status': 'success',
        'data': {
            'submission_id': submission,
            'total_tasks': len(l),
            'completed_tasks': count,
            'finished': completed
        }
    }
    return jsonify(response)


@app.route('/download/<submission>', methods=['GET'])
def download(submission):
    l = wr.List(submission+'_emails')
    records = export(l)

    filename = 'exports/' + submission + '.csv'
    with open(filename, 'wb', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['email', 'syntax', 'mx', 'deliverable', 'color', 'normalized'])
        writer.writerows(records)

    return send_file(filename, as_attachment=True)
