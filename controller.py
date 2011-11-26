import json
from beaker.middleware import SessionMiddleware
import bottle
from sqlalchemy.sql.expression import and_
from model import campaign, status, expensetypes, gaintypes, get_one, campaign_type_get_all, status_profile, init_db, profile, chat, chat_type, profile_types, PROFILE_OWNER, PROFILE_CONTACT

__author__ = 'rohan'

url_root = "/campaigns"
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
    if 'uid' in session and 'loggedin' in session:
        if session['loggedin'] == True:
            return True
    else:
        return False


def auth(check_func=validate_login):
    def decorator(view):
        def wrapper(*args, **kwargs):
            auth = check_func()
            if auth:
                return view(*args, **kwargs)
            return bottle.redirect(url_root + '/login.html')


        return wrapper

    return decorator


def logout():
    get_session().delete()


def login(user, passwd):
    db = init_db()
    user = db.query(profile).filter(and_(profile.name==user,profile.passwd==passwd)).first()
    if user:
        get_session()['uid'] = user.id
        get_session()['loggedin'] = True
    else:
        get_session().delete()


@post(url_root + '/login')
def handler():
    login(request.POST.get('user'), request.POST.get('passwd'))
    if not validate_login():
        bottle.redirect(url_root + '/login.html?err=invalid')
    bottle.redirect(url_root)


@get(url_root + '/logout')
def handler():
    logout()
    bottle.redirect(url_root)


@get(url_root)
@view('all_campaigns')
@auth()
def handler():
    db = init_db()
    sess = get_session()
    objs = db.query(campaign).filter(campaign.profiles.any(id=sess['uid'])).all()

    return dict(items=objs)


@get(url_root + '/:id')
@auth()
@view('single_campaign')
def handler(id):
    sess = get_session()
    db = init_db()
    obj = db.query(campaign).filter(and_(campaign.profiles.any(id=sess['uid']),campaign.id==id)).first()
    if(obj is None):
        bottle.redirect(url_root)

    types = campaign_type_get_all(exclude=obj.campaign_type)

    return dict(item=obj, ctypes=types, uattrs=json.loads(obj.attrs), gains=gaintypes, expenses=expensetypes,
                status=status, ugains=json.loads(obj.gains), uexpenses=json.loads(obj.expenses))


@get(url_root + '/:id/destroy')
@auth()
def handler(id):
    sess = get_session()
    db = init_db()
    obj = db.query(campaign).fiter(and_(campaign.profiles.any(id=sess['uid']),campaign.id==id)).first()
    if(obj is None):
        bottle.redirect(url_root)
    obj.delete(session=db)
    bottle.redirect(url_root)


@get(url_root + '/new')
@auth()
@view('new_campaign')
def handler():
    return dict(ctypes=campaign_type_get_all(), gains=gaintypes, expenses=expensetypes, status=status)


@post(url_root)
@auth()
def handler():
    db = init_db()
    obj = campaign()
    obj.update(request.POST,db)
    sess = get_session()
    current_profile = db.query(profile).filter(profile.id==sess['uid']).first()
    if current_profile:
        obj.profiles.append(current_profile)
        obj.save(session=db)
        current_profile.campaign.append(obj)
        current_profile.save(session=db)
    
    if(obj is None):
        return "error"
    bottle.redirect(url_root + '/' + str(obj.id))


@post(url_root + '/:id')
@auth()
def handler(id):
    db = init_db()
    sess = get_session()
    obj = db.query(campaign).fiter(and_(campaign.profiles.any(id=sess['uid']),campaign.id==id,campaign.uuid == request.POST.get('uuid'))).first()
    if(obj is None):
        bottle.redirect(url_root)
    obj.update(request.POST,session=db)

    bottle.redirect(url_root + '/' + id)


#/campaigns/:id/contacts/
url_root_contacts = url_root + "/contacts"

@get(url_root_contacts)
@auth()
@view("all_contacts")
def handler():
    sess = get_session()
    db = init_db()
    objs = db.query(campaign).filter(campaign.profiles.any(id=sess['uid'])).all()
    return dict(items=objs)


@get(url_root_contacts + "/new")
@view("new_contact")
@auth()
def handler():
    db = init_db()
    sess = get_session()
    campaigns = db.query(campaign.id,campaign.desc).filter(campaign.profiles.any(id=sess['uid'])).all()
    return dict(pstatuses=status_profile, campaigns=campaigns,type=profile_types.index(request.params.get('type') if 'type' in request.params else 'contact'))


@post(url_root_contacts)
@auth()
def handler():
    sess = get_session()
    db = init_db()
    obj = profile()
    obj.update(request.POST,session=db)
    if obj and 'campaign_id' in request.POST:

        camp = db.query(campaign).filter(and_(campaign.profiles.any(id=sess['uid']),campaign.id == request.POST.get('campaign_id'))).first()
        if camp:
            obj.campaign.append(camp)
            obj.save(session=db)

    bottle.redirect(url_root_contacts + '/' + str(obj.id)) if obj else bottle.redirect(url_root_contacts)


@get(url_root_contacts + "/:cid")
@auth()
@view('single_contact')
def handler(cid):
    db = init_db()
    obj = db.query(profile).filter(profile.id == cid).first()
    return dict(obj=obj,campaign=obj.campaign,pstatuses=status_profile) if obj else bottle.redirect(
        url_root_contacts)


@post(url_root_contacts + "/:cid")
@auth()
def handler(cid):
    db = init_db()
    obj = db.query(profile).filter(and_(profile.id == cid, profile.uuid == request.POST.get('uuid'))).first()
    if(obj is None):
        bottle.redirect(url_root_contacts)
    obj.update(request.POST,session=db)
    bottle.redirect(url_root_contacts + '/' + cid)


@get(url_root_contacts + '/:cid/chats')
@auth()
@view('all_chats')
def handler(cid):
    db = init_db()
    item = db.query(profile).filter(profile.id == cid).first()

    return dict(items=item,cid=cid)


@get(url_root_contacts + '/:cid/chats/new')
@auth()
@view('new_chat')
def handler(cid):
    return dict(profile_id=cid, chat_type=chat_type)


@post(url_root_contacts + '/:cid/chats')
@auth()
def handle(cid):
    db = init_db()
    obj = chat()
    prof = db.query(profile).filter(profile.id == cid).first()
    obj.update(request.POST,session=db)
    if prof:
        prof.chats.append(obj)
        prof.save(session=db)

    bottle.redirect(url_root_contacts + '/' + cid + '/chats/' + str(obj.id)) if obj else bottle.redirect(
        url_root_contacts)


@get(url_root_contacts + '/:cid/chats/:id')
@auth()
@view("single_chat")
def handler(cid, id):
    db = init_db()
    obj = db.query(chat).filter(chat.id == id).first()
    return dict(profile_id=cid, item=obj, chat_type=chat_type)


@post(url_root_contacts + '/:cid/chats/:id')
@auth()
def handler(cid, id):
    db = init_db()
    obj = db.query(chat).filter(chat.id == id).first()
    obj.update(request.POST,session=db)
    
    return bottle.redirect(url_root_contacts + '/%s/chats/%s' % (cid, id))