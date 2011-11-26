import json
from beaker.middleware import SessionMiddleware
import bottle
from sqlalchemy.sql.expression import and_
from model import campaign, status, expensetypes, gaintypes, get_all, get_one, campaign_type_get_all, status_profile, init_db, profile, chat, chat_type

__author__ = 'rohan'

url_root= "/campaigns"
ENV = ['Production', 'Development']

__author__ = 'rohan'
from bottle import route, request, get, post, view

bottle.debug(True)

session_opts = {
    'session.auto': True,
    'session.timeout': 180,
    'session.type': 'ext:database',
    'session.url': 'mysql://rohan:gotohome@localhost/ron',
    'session.key': 'campaignsession',
    'session.secret': 'gotohome',
    'session.lock_dir': './'
}
app = SessionMiddleware(bottle.app(), session_opts)

def get_session():
    return bottle.request.environ.get('beaker.session')


def validate_login():
    session = get_session()
    if 'user' in session and 'loggedin' in session:
        if session['loggedin'] == True:
            return True
    else:
        return False


def auth(check_func=validate_login):
    print "before handle"

    def decorator(view):
        def wrapper(*args, **kwargs):
            auth = check_func()
            if auth:
                return view(*args, **kwargs)
            return bottle.redirect(url_root+'/login.html')

        print "after handle"
        return wrapper

    return decorator


def logout():
    get_session().delete()


def login(user, passwd):
    if user == 'rohan' and passwd == 'gotohome':
        get_session()['user'] = user
        get_session()['loggedin'] = True
    else:
        get_session().delete()


@post(url_root+'/login')
def handler():
    login(request.POST.get('user'), request.POST.get('passwd'))
    if not validate_login():
        bottle.redirect(url_root+'/login.html?err=invalid')
    bottle.redirect(url_root)


@get(url_root+'/logout')
def handler():
    logout()
    bottle.redirect(url_root)


@get(url_root)
@view('all_campaigns')
@auth()
def handler():
    get_session()['ip'] = request.environ['REMOTE_ADDR']
    objs = get_all()
    print "last ip --> " + get_session()['ip']
    try:
        print "last id " + get_session()['id']
    except KeyError as e:
        pass
    return dict(items=objs)


@get(url_root+'/:id')
@auth()
@view('single_campaign')
def handler(id):
    obj = get_one(id)
    if(obj is None):
        bottle.redirect(url_root)
    
    types = campaign_type_get_all(exclude=obj.campaign_type)

    return dict(item=obj, ctypes=types, uattrs=json.loads(obj.attrs), gains=gaintypes, expenses=expensetypes,
                status=status, ugains=json.loads(obj.gains), uexpenses=json.loads(obj.expenses))


@get(url_root+'/:id/destroy')
@auth()
def handler(id):
    obj = get_one(id)
    if(obj is None):
        bottle.redirect(url_root)
    obj.delete()
    bottle.redirect(url_root)


@get(url_root+'/new')
@auth()
@view('new_campaign')
def handler():
    return dict(ctypes=campaign_type_get_all(), gains=gaintypes, expenses=expensetypes, status=status)


@post(url_root)
@auth()
def handler():
    obj = campaign()
    obj.update(request.POST)
    if(obj is None):
        return "error"
    bottle.redirect(url_root+'/' + str(obj.id))


@post(url_root+'/:id')
@auth()
def handler(id):
    obj = get_one(id, uuid=request.POST.get("uuid"))
    if(obj is None):
        bottle.redirect(url_root)
    obj.update(request.POST)
    print "after bk " + obj.desc
    bottle.redirect(url_root+'/' + id)


#/campaigns/:id/contacts/
url_root_contacts = url_root+"/contacts"
@get(url_root_contacts)
@auth()
@view("all_contacts")
def handler():
    contacts = init_db().query(profile).all()
    return dict(items=contacts)
@get(url_root_contacts+"/new")
@auth()
@view("new_contact")
def handler():
    campaigns = init_db().query(campaign.id,campaign.desc)
    return dict(pstatuses=status_profile,campaigns=campaigns)


@post(url_root_contacts)
@auth()
def handler():
    obj = profile()
    if obj:
        camp = get_one(request.POST.get('campaign_id'))
        if camp:
            obj.campaign = camp
            obj.save()
    obj.update(request.POST)
    bottle.redirect(url_root_contacts+'/'+str(obj.id)) if obj else bottle.redirect(url_root_contacts)


@get(url_root_contacts+"/:cid")
@auth()
@view('single_contact')
def handler(cid):
    obj = init_db().query(profile).filter(profile.id==cid).first()
    campaign_name = init_db().query(campaign.desc).filter(campaign.id==obj.id).first()
    return dict(obj=obj,campaign_name=campaign_name,pstatuses=status_profile) if obj else bottle.redirect(url_root_contacts)


@post(url_root_contacts+"/:cid")
@auth()
def handler(cid):
    obj = init_db().query(profile).filter(and_(profile.id==cid,profile.uuid==request.POST.get('uuid'))).first()
    if(obj is None):
        bottle.redirect(url_root_contacts)
    obj.update(request.POST)
    bottle.redirect(url_root_contacts+'/' + cid)


@get(url_root_contacts+'/:cid/chats')
@auth()
@view('all_chats')
def handler(cid):
    item = init_db().query(profile).filter(profile.id==cid).first()
    print item
    return dict(items=item)
@get(url_root_contacts+'/:cid/chats/new')
@auth()
@view('new_chat')
def handler(cid):
    return dict(profile_id=cid,chat_type=chat_type)
@post(url_root_contacts+'/:cid/chats')
@auth()
def handle(cid):
    db =init_db()
    obj = chat()
    prof = db.query(profile).filter(profile.id==cid).first()
    obj.update(request.POST)
    if prof:
        prof.chats.append(obj)
        db.add(prof)
        db.commit()


    bottle.redirect(url_root_contacts+'/'+cid+'/chats/'+str(obj.id)) if obj else bottle.redirect(url_root_contacts)
@get(url_root_contacts+'/:cid/chats/:id')
@auth()
@view("single_chat")
def handler(cid,id):
    obj = init_db().query(chat).filter(chat.id==id).first()
    return dict(profile_id=cid,item=obj,chat_type=chat_type)
@post(url_root_contacts+'/:cid/chats/:id')
@auth()
def handler(cid,id):
    db = init_db()
    obj = db.query(chat).filter(chat.id==id).first()
    obj.update(request.POST)
    db.add(obj)
    db.commit()
    return bottle.redirect(url_root_contacts+'/%s/chats/%s' %(cid,id))