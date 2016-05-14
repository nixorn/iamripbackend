from src.models import *
from src.engine import *
from src.app import app
from fixtures import fixtures 


def create_database():
    Base.metadata.create_all(engine)


def drop_database():
    Base.metadata.drop_all(engine)

def run_application():
    app.run(debug=True)

def load_fixtures():
    for model_name in ['User', 'Message', 'Timer', 'Source']:
        records = fixtures[model_name]
        model = globals()[model_name]
        for record in records:
            try:
                r = model(**record)
                session.add(r)
                session.commit()
            except:
                session.rollback()


import argparse
parser = argparse.ArgumentParser(description='Iamrip manage tool.')

subparsers = parser.add_subparsers(help='sub-commands', dest='subparser_name')

parser_database = subparsers.add_parser('database', help='database operations')
parser_database.add_argument('--recreate', action='store_true')
parser_database.add_argument('--load_fixtures', action='store_true')

parser_application = subparsers.add_parser('app', help='application manager')
parser_application.add_argument('--run', action='store_true')


if __name__ == '__main__':
    args = parser.parse_args()
    if args.subparser_name == 'database':
        if args.recreate:
            drop_database()
            create_database()
            load_fixtures()
        elif args.load_fixtures:
            load_fixtures()

    elif args.subparser_name == 'app':
        if args.run:
            run_application()
