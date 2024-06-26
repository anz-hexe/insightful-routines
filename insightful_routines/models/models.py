from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from insightful_routines.config import Config
from insightful_routines.models import Base

config = Config()

engine = create_engine(url=config.postgres_uri, echo=True)
Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
