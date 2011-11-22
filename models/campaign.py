import json
from models.base import Base
import datetime
import uuid
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import and_

__author__ = 'rohan'
from sqlalchemy import Column, Integer,String,Float,BigInteger

Base = declarative_base()
types = ['Google Adwords', 'Cold Email', 'Cold Call', 'Blog', 'Media', 'Forum activity', 'Twitter', 'White paper', 'Ebook','Facebook']

class campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer,primary_key=True,autoincrement=True,unique=True)
    uuid = Column(String(100),default=uuid.uuid4().__str__())
    desc = Column(String(200),default="New Campaign")
    cash_spent = Column(Float,default=0.0)
    revenue = Column(Float,default=0.0)
    conversions = Column(Integer,default=0)
    profit  = Column(Float,default=0.0)
    roi  = Column(Float,default=0.0)
    startTs = Column(BigInteger,default=0)
    endTs =     Column(BigInteger,default=0)
    time_spent = Column(Integer,default=0)  # store time in number of minutes , convert to hours at view
    campaign_type = Column(Integer)
    goal = Column(Integer)
    attrs = Column(String(1000),default=json.dumps({"empty":True})) # a json for all other unique attributes
    @hybrid_property
    def time_str(self):
        return "less than a hour" if (self.time_spent <= 1 or self.time_spent==0) else str(self.time_spent) + " hrs"
    @hybrid_property
    def campaign_desc(self):
        obj = campaign_type_get_one(self.campaign_type)
        if(obj is not None):
            return obj.desc
        return None
    def update(self,params):
        self.id = params.get('id') if params.get("id") is not None else self.id
        self.uuid = params.get('uuid') if params.get("uuid") is not None else self.uuid
        self.desc = params.get('desc') if params.get("desc") is not None else self.desc
        self.cash_spent = params.get('cash_spent') if params.get("cash_spent") is not None else self.cash_spent
        self.time_spent = params.get('time_spent') if params.get("time_spent") is not None else self.time_spent
        self.revenue = params.get('revenue') if params.get("revenue") is not None else self.revenue
        self.conversions = params.get('conversions') if params.get("conversions") is not None else self.conversions
        self.profit = params.get('profit') if params.get("profit") is not None else self.profit
        self.roi = params.get('roi') if params.get("roi") is not None else self.roi
        self.startTs = params.get('sts') if params.get("sts") is not None else self.startTs
        self.endTs = params.get('ets') if params.get("ets") is not None else self.endTs
        self.campaign_type = params.get('ctype') if params.get("ctype") is not None else self.campaign_type
        self.goal = params.get('goal') if params.get("goal") is not None else self.goal
        self.attrs = params.get('attrs') if params.get("attrs") is not None else self.attrs
        print "update "+self.desc
        db = init_db()
        db.add(self)
        db.commit()
        return self
    def delete(self):
        db = init_db()
        db.delete(self)
        db.commit()

class campaign_type(Base):
    __tablename__ = "campaign_types"
    id = Column(Integer,primary_key=True,autoincrement=True,unique=True)
    desc = Column(String(200),default="Default Type")
    details = Column(String(1000)) # a json describing extra attributes of this campaign type
def campaign_type_get_all(exclude=None):
    return init_db().query(campaign_type).filter(campaign_type.id !=exclude)
def campaign_type_get_one(typeid):
    return init_db().query(campaign_type).filter(campaign_type.id == typeid).first()
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

def get_all():
    return init_db().query(campaign).all()

def get_one(id,uuid=None):
    return init_db().query(campaign).filter(campaign.id==id).first() if uuid is None else init_db().query(campaign).filter(and_(campaign.id==id,campaign.uuid==uuid)).first()
if __name__ == "__main__":
    init_db()
