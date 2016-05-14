from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



Base = declarative_base()

engine = create_engine('postgresql+psycopg2://iamrip:iamrip@localhost:5432/iamrip', echo=True)

session = sessionmaker(bind=engine)()
