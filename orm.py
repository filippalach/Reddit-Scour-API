from sqlalchemy import Column, DateTime, Integer, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()

class Driver(Base):
    __tablename__ = 'drivers'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime())
    data = Column(JSON)

    def update(self, id=None, created=None, data=None):
        if created is not None:
            self.created = created
        if data is not None:
            self.data = data

    def dump(self):
        data = {
            'id': self.id,
            'created': self.created,
            'drivers': self.data
        }
        return data


def init_db(uri):
    engine = create_engine(uri, convert_unicode=True, echo=True)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)
    return db_session