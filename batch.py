import csv
import time

import redis
from rq import Queue

from models import push
from validate import validate

conn = redis.from_url('redis://127.0.0.1:6379')
q = Queue(connection=conn)


def task(email):
    response = validate(email)
    push(response)
    return response


def process(input_file):
    enqueued = 0
    with open(input_file, newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if row[0]:
                q.enqueue_call(func='batch.task', args=(row[0],), result_ttl=7200, timeout=30)
                enqueued = enqueued + 1
                print(f'[*] Enqueued jobs: {enqueued}')


def main():
    input_file = input('[*] Input CSV file: ')
    start = time.time()
    process(input_file)
    end = time.time()
    print(f'[*] Done. Time elapsed: {end - start} seconds.')


if __name__ == '__main__':
    main()
