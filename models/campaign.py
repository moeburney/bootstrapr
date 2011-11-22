from models.base import Base
import datetime
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

__author__ = 'rohan'
from sqlalchemy import Column, Integer,String,Float,BigInteger

Base = declarative_base()
types = ['Google Adwords', 'Cold Email', 'Cold Call', 'Blog', 'Media', 'Forum activity', 'Twitter', 'White paper', 'Ebook','Facebook']

class campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer,primary_key=True,autoincrement=True,unique=True)
    desc = Column(String(200),default="New Campaign")
    cash_spent = Column(Float,default=0.0,unique=True)
    time_spent = Column(BigInteger)
    revenue = Column(Float,default=0.0)
    conversions = Column(Integer,default=0)
    profit  = Column(Float,default=0.0)
    roi  = Column(Float,default=0.0)
    startTs = Column(BigInteger,default=int(datetime.datetime.now().strftime("%s")) * 1000)
    endTs =     Column(BigInteger)
    campaign_type = Column(Integer)
    goal = Column(Integer)
    attrs = Column(String(1000)) # a json for all other unique attributes

class campaign_type(Base):
    __tablename__ = "campaign_types"
    id = Column(Integer,primary_key=True,autoincrement=True,unique=True)
    desc = Column(String(200),default="Default Type")
    details = Column(String(1000)) # a json describing extra attributes of this campaign type
def init_db(transactional=False):
    engine = create_engine("mysql://rohan:gotohome@localhost/ron")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    if(session.query(campaign_type).count() <=0):
        for temp in types:
            session.add(campaign_type(desc=temp))
    session.commit()
    return session


if __name__ == "__main__":
    init_db()
