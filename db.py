# http://www.web2py.com/books/default/chapter/29/06/the-database-abstraction-layer
from pydal import DAL, Field
from datetime import datetime

db = DAL('sqlite://levels.sqlite')

db.define_table('level',
    Field('filename'),
    Field('reclink'),
    Field('hiscore', 'double', default=0),
    Field('maxplaytime', 'double'),
    Field('created', 'datetime', default=datetime.now()),
)

db.define_table('sequence',
    Field('level', 'reference level'),
    Field('hiscore', 'double'),
    Field('episodes', 'integer'),
    Field('seed', 'integer'),
    Field('actions', 'list:integer'),
    Field('created', 'datetime', default=datetime.now()),
)

db.define_table('setting',
    Field('name'),
    Field('str_value'),
    Field('int_value', 'integer'),
    Field('int_values', 'list:integer'),
    Field('created', 'datetime', default=datetime.now()),
)


def print_levels():
    for row in db(db.level.id > -1).select():
        print(row)

def print_sequences():
    for row in db(db.sequence.id > -1).select():
        print(row)

def print_settings():
    for row in db(db.setting.id > -1).select():
        print(row)

if __name__ == '__main__':
    print_settings()
    print()
    print_sequences()
    print()
    print_levels()

"""
def votes( votee=None ):
    if votee:
        query = db.vote.votee == votee.lower()
    else:
        query = db.vote.id > -1

    rows = db(query).select().as_list()
    count = len( rows )
    total = sum( row['score'] for row in rows )
    avg = total/count if count else 0

    for row in rows:
        print(row)

    print("count: %d votes" % (count))
    print("avg: %.2f" % (avg))
"""