from peewee import *
from playhouse.dataset import DataSet

db = SqliteDatabase('validator.db')
ds = DataSet('sqlite:///validator.db')


class EmailInfo(Model):
    email = CharField(index=True, unique=True)
    syntax = BooleanField()
    mx = BooleanField(null=True)
    deliverable = BooleanField(null=True)
    color = CharField()
    normalized = CharField(null=True)

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
    instance, created = EmailInfo.get_or_create(email=record['email'], defaults=record)
    instance.save()
    if created:
        print('[*] New record: {}'.format(record['email']))
    else:
        print('[*] Updated record: {}'.format(record['email']))
    return created


def export(emails):
    records = []
    for email in emails:
        i = EmailInfo.get_or_none(EmailInfo.email == email)
        if i:
            records.append([i.email, i.syntax, i.mx, i.deliverable, i.color, i.normalized])
    return records


db.connect()
db.create_tables([EmailInfo])
db.close()
