import json
import profile
import uuid
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.sql.expression import and_
from sqlalchemy.types import Integer, String, BigInteger, Float
import time
engine = create_engine("mysql://rohan:gotohome@localhost/ron")
Base = declarative_base()
profile_types = ['owner', 'contact']
status_profile = ['Prospect', 'Subscriber', 'Paid user']
STATUS_PROFILE_PROSPECT = 0
STATUS_PROFILE_SUBSCRIBER = 1
STATUS_PROFILE_PAIDUSER = 2
PROFILE_OWNER = 0
PROFILE_CONTACT = 1

__author__ = 'rohan'

ctypes = ['Google Adwords', 'Cold Email', 'Cold Call', 'Blog', 'Media', 'Forum activity', 'Twitter', 'White paper',
          'Ebook', 'Facebook']
gaintypes = ['Conversions', 'Mailing List Subscriptions', 'Sales', 'Views', 'Interactions', 'Revenue']
expensetypes = ['Time Spent', 'Money Spent']
status = ['Finished', 'Pending', 'Ongoing']
STATUS_FINISHED = 0
STATUS_PENDING = 1
STATUS_ONGOING = 2
CASH = 1
TIME = 0
CONVERSIONS = 0
MAILSUBS = 1
SALES = 2
VIEWS = 3
INTERACTIONS = 4
REVENUE = 5
chat_type = ['email', 'social media', 'call', 'physical']
CHAT_EMAIL = 0
CHAT_SOCIAL_MEDIA = 1
CHAT_CALL = 2
CHAT_PHYSICAL = 3

class campaign_type(Base):
    __tablename__ = "campaign_types"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    desc = Column(String(200), default="Default Type")
    details = Column(String(1000)) # a json describing extra attributes of this campaign type

link_table = Table('association', Base.metadata,
                   Column('campaign_id', Integer, ForeignKey('campaigns.id')),
                   Column('profile_id', Integer, ForeignKey('profiles.id'))
)

class campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(String(100), default=uuid.uuid4().__str__())
    desc = Column(String(200), default="New Campaign")
    gains = Column(String(1000), default="{}") #store gain types and their monetary weights
    startTs = Column(BigInteger, default=0)
    endTs = Column(BigInteger, default=0)
    campaign_type = Column(Integer)
    goal = Column(Integer)
    roi = Column(Integer, default=0)
    rank = Column(Integer, default=0)
    expenses = Column(String(1000), default="{}")
    attrs = Column(String(1000), default="{}") # a json for all other unique attributes
    notes = Column(String(1000))
    status = Column(Integer, default=STATUS_PENDING)
    profiles = relationship("profile", backref="campaigns", cascade="all", secondary=link_table)

    @hybrid_property
    def outgo(self):
        outtemp = json.loads(self.expenses)
        res = 0
        for k, v in outtemp.iteritems():
            if('unitexpense' in v):
                res += int(v['unitexpense']) * int(v['quantity'])
            else:
                res += int(v['quantity'])
        return res

    @hybrid_property
    def incomes(self):
        intemp = json.loads(self.gains)
        res = 0
        for k, v in intemp.iteritems():
            if('unitgain' in v):
                res += int(v['unitgain']) * int(v['quantity'])
            else:
                res += int(v['quantity'])

        return res

    @hybrid_property  #todo , ask in irc if hybric property can be stored in db
    def roi(self):
        return self.incomes - self.outgo

    @hybrid_property
    def rank(self):
        db = init_db()
        roidict = dict()
        for obj in db.query(campaign.uuid, campaign.roi).all():
            roidict[obj.uuid] = obj.roi
        ranked = sorted(roidict, key=lambda obj:obj.roi)
        return ranked.index(self.uuid)


    @hybrid_property
    def campaign_desc(self):
        obj = campaign_type_get_one(self.campaign_type)
        if(obj is not None):
            return obj.desc
        return None

    def update(self, params):
        self.id = params.get('id') if 'id' in params else self.id
        self.uuid = params.get('uuid') if 'uuid' in params else self.uuid
        self.desc = params.get('desc') if 'desc' in params else self.desc
        self.gains = params.get('gains') if 'gains' in params else self.gains
        self.expenses = params.get('expenses') if 'expenses' in params else self.expense
        self.startTs = params.get('sts') if "sts" in params else self.startTs
        self.endTs = params.get('ets') if "ets" in params else self.endTs
        self.campaign_type = params.get('ctype') if "ctype" in params else self.campaign_type
        self.goal = params.get('goal') if "goal" in params else self.goal
        self.attrs = params.get('attrs') if "attrs" in params else self.attrs
        self.notes = params.get('notes') if "notes" in params else self.notes
        self.status = params.get('status') if "status" in params else self.status
        print "update blast " + self.desc
        db = init_db()
        db.add(self)
        db.commit()

    def delete(self):
        db = init_db()
        db.delete(self)
        db.commit()

class chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(String(100), default=uuid.uuid4().__str__())
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    ts = Column(Float, default=time.time())
    content = Column(String(500), default="No Comments")
    type = Column(Integer)
    details = Column(String(500), default="{}")
    parent_chat = Column(Integer, ForeignKey(id))
    replies = relationship("chat", backref=backref("topic", remote_side=[id]))
    

    def update(self, params):
        self.id = params.get('id') if 'id' in params else self.id
        self.uuid = params.get('uuid') if 'uuid' in params else self.uuid
        self.profile_id = params.get('profile_id') if 'profile_ud' in params else self.profile_id
        self.ts = params.get('ts') if 'ts' in params else self.ts
        self.content = params.get('content') if 'content' in params else self.content
        self.type = params.get('type') if 'type' in params else self.type
        self.parent_chat = params.get('parent_chat') if 'parent_chat' in params else self.parent_chat
        self.details = params.get('details') if 'details' in params else self.details

    def delete(self):
        db = init_db()
        db.delete(self)
        db.commit()


class profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(String(100), default=uuid.uuid4().__str__())
    name = Column(String(200), default="New Profile")
    pemail = Column(String(50))
    campaign_id = Column(Integer, ForeignKey(campaign.id))
    profile_type = Column(Integer, default=PROFILE_CONTACT, nullable=False)
    status = Column(Integer, default=STATUS_PROFILE_PROSPECT)
    chats = relationship("chat", backref="profile", cascade="all, delete-orphan")

    def update(self, params):
        self.id = params.get('id') if 'id' in params else self.id
        self.uuid = params.get('uuid') if 'uuid' in params else self.uuid
        self.name = params.get('name') if 'name' in params else self.name
        self.pemail = params.get('pemail') if 'pemail' in params else self.pemail
        self.campaign_id = params.get('campaign_id') if 'campaign_id' in params else self.campaign_id
        self.profile_type = params.get('ptype') if 'ptype' in params else self.profile_type
        self.status = params.get('pstatus') if 'pstatus' in params else self.status
        print "update profile " + self.desc
        db = init_db()
        db.add(self)
        db.commit()

    def delete(self):
        db = init_db()
        db.delete(self)
        db.commit()


def profile_get_all():
    return init_db().query(profile).all()


def profile_get_all_by(campaign_id):
    return get_one(campaign_id).profiles


def profile_get_one(profile_id, profile_uuid=None):
    return init_db().query(profile).filter(
        profile.id == profile_id).first() if profile_uuid is None else init_db().query(profile).filter(
        and_(profile.id == profile_id, profile.uuid == profile_uuid)).first()

def init_db(transactional=False):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
def get_all():
    return init_db().query(campaign).all()


def get_one(id, uuid=None):
    return init_db().query(campaign).filter(campaign.campaign.id == id).first() if uuid is None else init_db().query(
        campaign.campaign).filter(and_(campaign.campaign.id == id, campaign.campaign.uuid == uuid)).first()

def campaign_type_get_all(exclude=None):
    return init_db().query(campaign.campaign_type).filter(campaign.campaign_type.id != exclude)


def campaign_type_get_one(typeid):
    return init_db().query(campaign.campaign_type).filter(campaign.campaign_type.id == typeid).first()

if __name__ == "__main__":
    init_db()
