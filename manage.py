from src.models import *
from src.engine import *
from src.app import app


def create_database():
    Base.metadata.create_all(engine)


def drop_database():
    Base.metadata.drop_all(engine)

def run_application():
    app.run(debug=True)


import argparse
parser = argparse.ArgumentParser(description='Iamrip manage tool.')

subparsers = parser.add_subparsers(help='sub-commands', dest='subparser_name')

parser_database = subparsers.add_parser('database', help='database operations')
parser_database.add_argument('--drop', action='store_true')
parser_database.add_argument('--create', action='store_true')

parser_application = subparsers.add_parser('app', help='application manager')
parser_application.add_argument('--run', action='store_true')


if __name__ == '__main__':
    args = parser.parse_args()
    if args.subparser_name == 'database':
        if args.drop:
            drop_database()
        if args.create:
            create_database()
    elif args.subparser_name == 'app':
        if args.run:
            run_application()
