from peewee import *

db = SqliteDatabase('validator.db')


class EmailInfo(Model):
    email = CharField(index=True, unique=True)
    syntax = BooleanField()
    mx = BooleanField()
    deliverable = BooleanField()
    color = CharField()
    normalized = CharField()

    class Meta:
        database = db


def pull(email):
    record = EmailInfo.get_or_none(EmailInfo.email == email)
    if not record:
        return None

    result = {
        'email': record.email,
        'syntax': record.syntax,
        'mx': record.mx,
        'deliverable': record.deliverable,
        'color': record.color,
        'normalized': record.normalized
    }
    return result


def push(record):
    EmailInfo.create(email=record['email'], syntax=record['syntax'], mx=record['mx'], deliverable=record['deliverable'],
                     color=record['color'], normalized=record['normalized'])
    count = EmailInfo.select().count()
    print(f'[*] New record added to database: {record["email"]}. Total count: {count}.')


db.connect()
db.create_tables([EmailInfo])
db.close()
