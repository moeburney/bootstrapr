import email
import json
import pickle
import re
import string
import uuid
from sqlalchemy.engine import create_engine, reflection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import Column, Table, ForeignKey, DropTable, DropConstraint, ForeignKeyConstraint, MetaData
from sqlalchemy.sql.expression import and_
from sqlalchemy.types import Integer, String, BigInteger, Float, Text
import time

engine = create_engine("mysql://rohan:gotohome@localhost/ron")
Base = declarative_base()
Session = sessionmaker(bind=engine)
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
chat_type = ['Phone', 'Physical']
CHAT_CALL = 0
CHAT_PHYSICAL = 1
CHAT_EMAIL = 2
CHAT_SOCIALMEDIA = 3



FEEDBACK_TYPE= ["Suggestion","Feature"]
FEEDBACK_SUGGESTION = FEEDBACK_TYPE.index("Suggestion")
FEEDBACK_FEATURE = FEEDBACK_TYPE.index("Feature")


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
    profiles = relationship("profile", backref="campaigns",
                            secondary=link_table)

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

    def update(self, params, session):
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

        db = session
        db.add(self)
        db.commit()

    def delete(self, session):
        db = session
        db.delete(self)
        db.commit()

    def save(self, session):
        db = session
        db.add(self)
        db.commit()


class chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(String(100), default=uuid.uuid4().__str__())
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    ts = Column(Float, default=time.time())
    subject = Column(String(50))
    content = Column(Text, default="No Comments")
    type = Column(Integer)
    details = Column(Text, default="{}")
    parent_chat = Column(Integer, ForeignKey(id))
    profile = relationship("profile", back_populates="chats")
    replies = relationship("chat", backref=backref("topic", remote_side=[id], order_by="chat.ts"))

    def update(self, params, session):
        self.id = params.get('id') if 'id' in params else self.id
        self.uuid = params.get('uuid') if 'uuid' in params else self.uuid
        self.profile_id = params.get('profile_id') if 'profile_ud' in params else self.profile_id
        self.ts = params.get('ts') if 'ts' in params else self.ts
        self.content = params.get('content') if 'content' in params else self.content
        self.type = params.get('type') if 'type' in params else self.type
        self.parent_chat = params.get('parent_chat') if 'parent_chat' in params else self.parent_chat
        self.details = params.get('details') if 'details' in params else self.details
        self.subject = params.get('subject') if 'subject' in params else self.subject
        db = session
        db.add(self)
        db.commit()

    def delete(self, session):
        db = session
        db.delete(self)
        db.commit()

    def save(self, session):
        db = session
        db.add(self)
        db.commit()

"""mail['id'] = msg['Message-ID'].strip().strip("<").strip(">")
mail['to'] = msg['to'].split('<')[1].strip('>')
mail['from'] = msg['from'].split('<')[1].strip('>')
mail['date'] = msg['date']
mail['body'] = body
mail['subject'] = msg['subject']
mail['parent'] = msg['In-Reply-To'].strip().strip("<").strip(">") if "In-Reply-To" in msg else None"""

def makechatfromemail(email):
    temp = chat()
    temp.details = json.dumps(email)
    if email['date'] is not None:
        stemp = email['date'].split(" ")[-1]
        temp.ts = time.mktime(time.strptime(email['date'], "%a, %d %b %Y %H:%M:%S " + stemp))

    temp.content = email['body']
    temp.subject = email['subject']
    temp.type = CHAT_EMAIL
    return temp

class feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(String(100), default=uuid.uuid4().__str__())
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    desc = Column(Text,default="New Feedback")
    type = Column(Integer,nullable=False)
    action = Column(Text,nullable=False)
    ts = Column(Float, default=time.time())
    status = Column(Integer,nullable=False,default=STATUS_PENDING)
    details = Column(Text,default="{}")
    profile = relationship("profile", back_populates="feedbacks")
    def update(self, params, session):
        self.id = params.get('id') if 'id' in params else self.id
        self.uuid = params.get('uuid') if 'uuid' in params else self.uuid
        self.profile_id = params.get('profile_id') if 'profile_ud' in params else self.profile_id
        self.ts = params.get('ts') if 'ts' in params else self.ts
        self.desc = params.get('desc') if 'desc' in params else self.desc
        self.type = params.get('type') if 'type' in params else self.type
        self.details = params.get('details') if 'details' in params else self.details
        self.action = params.get('action') if 'action' in params else self.action
        self.status = params.get('status') if 'status' in params else self.status
        db = session
        db.add(self)
        db.commit()

    def delete(self, session):
        db = session
        db.delete(self)
        db.commit()

    def save(self, session):
        db = session
        db.add(self)
        db.commit()
class profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(String(100), default=uuid.uuid4().__str__())
    name = Column(String(200), default="New Profile")
    passwd = Column(String(20), default=None)
    pemail = Column(String(50))
    profile_type = Column(Integer, default=PROFILE_CONTACT, nullable=False)
    status = Column(Integer, default=STATUS_PROFILE_PROSPECT)
    chats = relationship("chat", back_populates="profile", cascade="all, delete-orphan",order_by="chat.ts")
    feedbacks = relationship("feedback",back_populates="profile",cascade="all,delete-orphan",order_by="feedback.ts")
    campaign = relationship("campaign", backref="profile", secondary=link_table)
    g_oauth_token = Column(String(55))
    g_oauth_token_secret = Column(String(55))
    t_oauth_token = Column(String(55))
    t_oauth_token_secret = Column(String(55))
    twitter= Column(String(21))
    @hybrid_property
    def latest(self):
        if self.chats:
            contents = self.chats[0].content # chats are already sorted by time stamp
            words = re.findall(r'\w+', contents)
            if words:
                return string.join(words[:4])

    def update(self, params, session):
        self.id = params.get('id') if 'id' in params else self.id
        self.uuid = params.get('uuid') if 'uuid' in params else self.uuid
        self.name = params.get('name') if 'name' in params else self.name
        self.passwd = params.get('passwd') if 'passwd' in params else self.passwd
        self.pemail = params.get('pemail') if 'pemail' in params else self.pemail
        self.profile_type = params.get('ptype') if 'ptype' in params else self.profile_type
        self.status = params.get('pstatus') if 'pstatus' in params else self.status
        self.twitter = params.get('twitter') if 'twitter' in params else self.twitter
        db = session
        db.add(self)
        db.commit()

    def delete(self, session):
        db = session
        db.delete(self)
        db.commit()

    def save(self, session):
        db = session
        db.add(self)
        db.commit()


def profile_get_all():
    return init_db().query(profile).all()


def profile_get_all_by(campaign_id):
    return get_one(campaign_id).profiles


def profile_get_one(profile_id, profile_uuid=None):
    return init_db().query(profile).filter(
        profile.id == profile_id).first() if profile_uuid is None else init_db().query(profile).filter(
        and_(profile.id == profile_id, profile.uuid == profile_uuid)).first()


def drop_all():
    conn = engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.

    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(
                ForeignKeyConstraint((), (), name=fk['name'])
            )
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))

    trans.commit()


def init_db(transactional=False):
    session = Session()
    Base.metadata.create_all(engine)
    if((session.query(campaign_type).count()) <= 0):
        for temp in ctypes:
            session.add(campaign_type(desc=temp))
    if((session.query(profile).filter(profile.name == "admin").count()) <= 0):
        obj = profile()
        obj.name = "admin"
        obj.passwd = "admin"
        obj.pemail = "admin@admin.com"
        obj.profile_type = PROFILE_OWNER
        session.add(obj)
    session.commit()
    return session


def get_all():
    return init_db().query(campaign).all()


def get_one(id, uuid=None):
    return init_db().query(campaign).filter(campaign.id == id).first() if uuid is None else init_db().query(
        campaign).filter(and_(campaign.id == id, campaign.uuid == uuid)).first()


def campaign_type_get_all(exclude=None):
    return init_db().query(campaign_type).filter(campaign_type.id != exclude)


def campaign_type_get_one(typeid):
    return init_db().query(campaign_type).filter(campaign_type.id == typeid).first()


def emails(conn, email, since="1-JAN-1970"):
    mail = []
    status, response = conn.search(None, '(OR FROM "%s" TO "%s" SENTSINCE %s)' % (email, email, since))
    email_ids = [e_id for e_id in response[0].split()]
    print 'Number of emails from %s: since %s %i. IDs: %s' % (email, since, len(email_ids), email_ids)
    for x in email_ids:
        currmail = get_email(conn, x)
        if currmail is not None:
            print "adding mail "+currmail['subject']
            mail.append(currmail)

    mail.reverse()
    output = open('/home/rohan/data.pkl', 'wb')
    pickle.dump(mail, output)
    for y in mail:
        print "=======######## GOt email "+(y['subject'] if 'subject' in y else "NO SUBJECT") +"  mid "+(y['id'] if 'id' in y else "NO ID") + "  parent id "+(y['parent'] if ('parent' in y and y['parent'] is not None) else "NO PARENT")
        db = init_db()
        contact = db.query(profile).filter(profile.pemail == email).first()
        currchat = makechatfromemail(y)
        if not contact.chats:
            currchat.save(session=db)
            contact.chats.append(currchat)
            contact.save(session=db)
            print "save single email"
            continue
        contact.chats.sort(key=lambda x:x.ts)
        for old in contact.chats:
            if old['id'] == y['id']:
                continue
            if old.type == CHAT_EMAIL:
                obj = json.loads(old.details)
                print "OLD email "+(obj['subject'] if 'subject' in obj else "NO SUBJECT") +"  mid "+(obj['id'] if 'id' in obj else "NO ID" )+ "  parent id "+(obj['parent'] if ('parent' in obj and  obj['parent'] is not None) else "NO PARENT")
                if obj['id'] == (y['parent'] if 'parent' in y else ""):
                    print "EMAIL " + y['id'] + " is reply to " + old['id']
                    old.replies.append(currchat)
                    old.save(session=db)
                    currchat.save(session=db)
                    contact.chats.append(currchat)
                    contact.save(session=db)
                    continue
                currchat.save(session=db)
                contact.chats.append(currchat)
                contact.save(session=db)
    return


def get_email(conn, email_id):
    mail = {}
    _, response = conn.fetch(email_id, '(RFC822)')
    msg = email.message_from_string(response[0][1])
    body = get_first_text_part(msg)
    if "<" in msg['Message-ID']:
        mail['id'] = msg['Message-ID'].strip().strip("<").strip(">")
    if "<" in msg['to']:
        mail['to'] = msg['to'].split('<')[1].strip('>')
    if "<" in msg['from']:
        mail['from'] = msg['from'].split('<')[1].strip('>')
    mail['date'] = msg['date']
    mail['body'] = body
    mail['subject'] = msg['subject']
    if msg['parent'] is not None:
        if "<" in msg['parent']:
            mail['parent'] = msg['In-Reply-To'].strip().strip("<").strip(">") if "In-Reply-To" in msg else None
    return mail


def get_first_text_part(msg):
    maintype = msg.get_content_type()
    if maintype == "multipart/mixed" or maintype == "multipart/alternative":
        for part in msg.get_payload():
            if part.get_content_type() == "text/plain":
                return part.get_payload()
            else:
                for x in part.get_payload():
                    if x.get_content_type() == "text/plain":
                        return x.get_payload()
    elif maintype == 'text/plain':
        return msg.get_payload()

if __name__ == "__main__":
    init_db()
