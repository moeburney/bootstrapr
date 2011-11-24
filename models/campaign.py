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
ctypes = ['Google Adwords', 'Cold Email', 'Cold Call', 'Blog', 'Media', 'Forum activity', 'Twitter', 'White paper', 'Ebook','Facebook']
gaintypes = ['Conversions','Mailing List Subscriptions','Sales','Views','Interactions','Revenue']
expensetypes = ['Time Spent','Money Spent']
status = ['Finished','Pending','Ongoing']
STATUS_FINISHED=0
STATUS_PENDING=1
STATUS_ONGOING=2
CASH=1
TIME=0
CONVERSIONS=0
MAILSUBS=1
SALES=2
VIEWS=3
INTERACTIONS=4
REVENUE=5



class campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer,primary_key=True,autoincrement=True,unique=True)
    uuid = Column(String(100),default=uuid.uuid4().__str__())
    desc = Column(String(200),default="New Campaign")
    gains = Column(String(1000),default="{}") #store gain types and their monetary weights
    startTs = Column(BigInteger,default=0)
    endTs =     Column(BigInteger,default=0)
    campaign_type = Column(Integer)
    goal = Column(Integer)
    roi = Column(Integer,default=0)
    rank = Column(Integer,default=0)
    expenses = Column(String(1000),default="{}")
    attrs = Column(String(1000),default="{}") # a json for all other unique attributes
    notes = Column(String(1000))
    status = Column(Integer,default=STATUS_PENDING)

    @hybrid_property  #todo , ask in irc if hybric property can be stored in db
    def roi(self):
        outtemp = json.loads(self.expenses)
        intemp = json.loads(self.gains)
        res=0
        for k,v in intemp.iteritems():
            if('unitgain' in v):
                res += int(v['unitgain'])*int(v['quantity'])
            else:
                res += int(v['quantity'])
        for k,v in outtemp.iteritems():
            if('unitexpense' in v):
                res -= int(v['unitexpense'])*int(v['quantity'])
            else:
                res -= int(v['quantity'])
        return res
    @hybrid_property
    def rank(self):
        db = init_db()
        roidict = dict()
        for obj in db.query(campaign.uuid,campaign.roi).all():
            roidict[obj.uuid] = obj.roi
        ranked = sorted(roidict,key=lambda obj:obj.roi)
        return ranked.index(self.uuid)
        
            
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
        self.gains = params.get('gains') if params.get("gains") is not None else self.gains
        self.expenses = params.get('expenses') if params.get("expenses") is not None else self.expense
        self.startTs = params.get('sts') if params.get("sts") is not None else self.startTs
        self.endTs = params.get('ets') if params.get("ets") is not None else self.endTs
        self.campaign_type = params.get('ctype') if params.get("ctype") is not None else self.campaign_type
        self.goal = params.get('goal') if params.get("goal") is not None else self.goal
        self.attrs = params.get('attrs') if params.get("attrs") is not None else self.attrs
        self.notes = params.get('notes') if params.get("notes") is not None else self.notes
        self.status = params.get('status') if params.get("status") is not None else self.status
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
        for temp in ctypes:
            session.add(campaign_type(desc=temp))
        session.commit()

    return session

def get_all():
    return init_db().query(campaign).all()

def get_one(id,uuid=None):
    return init_db().query(campaign).filter(campaign.id==id).first() if uuid is None else init_db().query(campaign).filter(and_(campaign.id==id,campaign.uuid==uuid)).first()
if __name__ == "__main__":
    init_db()
