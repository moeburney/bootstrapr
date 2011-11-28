from _collections import defaultdict
import string
import datetime
import oauth2.clients.imap as imaplib
import json
import urllib
import urlparse
from beaker.middleware import SessionMiddleware
import bottle
from sqlalchemy.sql.expression import and_, desc, asc
import time
from model import campaign, status, expensetypes, gaintypes, campaign_type_get_all, status_profile, init_db, profile, chat, chat_type, profile_types, emails, CHAT_EMAIL, FEEDBACK_TYPE, feedback
import oauth2 as oauth
__author__ = 'rohan'

url_root = "/campaigns"
ENV = ['Production', 'Development']

__author__ = 'rohan'
from bottle import route, request, get, post, view

bottle.debug(True)


##OAUTH STUFF
GOOGLE_REQUEST_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetRequestToken'
GOOGLE_ACCESS_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetAccessToken'
GOOGLE_AUTHORIZATION_URL = 'https://www.google.com/accounts/OAuthAuthorizeToken'
GOOGLE_CALLBACK_URL = 'http://k4nu.com/campaigns/g/oauth'
GOOGLE_CONSUMER_KEY = "anonymous"
GOOGLE_CONSUMER_SECRET = "anonymous"
GOOGLE_SCOPE = "https://mail.google.com/"
GOOGLE_RESOURCE_URL = "https://mail.google.com/mail/b/%s/imap/"
GOOGLE_consumer = oauth.Consumer(GOOGLE_CONSUMER_KEY,GOOGLE_CONSUMER_SECRET)
GOOGLE_client = oauth.Client(GOOGLE_consumer)
GOOGLE_xoauth_displayname = "kkr"




##TWITTER OAUTH
TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TWITTER_AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
TWITTER_CALLBACK_URL = 'http://k4nu.com/campaigns/t/oauth'
TWITTER_CONSUMER_KEY = "jL2l985ZHPYiRC5I4IOlzg"
TWITTER_CONSUMER_SECRET = "hcVxPzghKsZNyHDy8YSzTyiFhIJ7S30Ajw7KX4Bas"
TWITTER_consumer = oauth.Consumer(TWITTER_CONSUMER_KEY,TWITTER_CONSUMER_SECRET)
TWITTER_client = oauth.Client(TWITTER_consumer)






session_opts = {
    'session.auto': True,
    'session.timeout': 3000,
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

@get(url_root+'/t/start_oauth')
def handler():
    global TWITTER_client
    url = TWITTER_REQUEST_TOKEN_URL+'?oauth_callback=%s' % (TWITTER_CALLBACK_URL)
    resp, content = TWITTER_client.request(url, 'GET')
    try:
        oauth_token = urlparse.parse_qs(content)['oauth_token'][0]
    except:
        TWITTER_client = oauth.Client(TWITTER_consumer)
        bottle.redirect(url_root)
    print "request token "+oauth_token
    oauth_token_secret = urlparse.parse_qs(content)['oauth_token_secret'][0]
    print "request secret "+oauth_token_secret
    TWITTER_client.token = oauth.Token(oauth_token, oauth_token_secret)
    if resp['status'] == '200':
        print 'OAuthGetRequestToken OK'
    else:
        print 'OAuthGetRequestToken status: %s' % resp['status']
        print content
    url = TWITTER_AUTHORIZATION_URL+'?oauth_token=%s' % urllib.quote_plus(oauth_token)
    bottle.redirect(url)

    return

@route(url_root+'/t/oauth',Methods=['GET','POST'])
def handler():
    url = TWITTER_ACCESS_TOKEN_URL+'?oauth_token=%s&oauth_verifier=%s' % (request.GET.get('oauth_token'),request.GET.get('oauth_verifier'))
    resp, content = TWITTER_client.request(url, 'GET')
    if resp['status'] == '200':
        print 'OAuthGetAccessToken OK'
        db = init_db()
        curr_uid = get_session()['uid']
        curr_profile = db.query(profile).filter(profile.id==curr_uid).first()
        if curr_profile:
            curr_profile.t_oauth_token = urlparse.parse_qs(content)['oauth_token'][0]
            curr_profile.t_oauth_token_secret = urlparse.parse_qs(content)['oauth_token_secret'][0]
            curr_profile.save(session=db)
        bottle.redirect(url_root)
    else:
        print 'OAuthGetAccessToken status: %s' % resp['status']
        print content
        bottle.redirect(url_root)

@get(url_root+'/g/start_oauth')
def handler():
    global GOOGLE_client
    url = GOOGLE_REQUEST_TOKEN_URL+'?scope=%s&oauth_callback=%s&xoauth_displayname=%s' % (GOOGLE_SCOPE, GOOGLE_CALLBACK_URL, GOOGLE_xoauth_displayname)
    resp, content = GOOGLE_client.request(url, 'GET')
    try:
        oauth_token = urlparse.parse_qs(content)['oauth_token'][0]
    except:
        GOOGLE_client = oauth.Client(GOOGLE_consumer)
        bottle.redirect(url_root)
    print "request token "+oauth_token
    oauth_token_secret = urlparse.parse_qs(content)['oauth_token_secret'][0]
    print "request secret "+oauth_token_secret
    GOOGLE_client.token = oauth.Token(oauth_token, oauth_token_secret)
    if resp['status'] == '200':
        print 'OAuthGetRequestToken OK'
    else:
        print 'OAuthGetRequestToken status: %s' % resp['status']
        print content
    url = GOOGLE_AUTHORIZATION_URL+'?hd=default&oauth_token=%s' % urllib.quote_plus(oauth_token)
    bottle.redirect(url)

    return

@route(url_root+'/g/oauth',Methods=['GET','POST'])
def handler():
    url = GOOGLE_ACCESS_TOKEN_URL+'?oauth_token=%s&oauth_verifier=%s' % (request.GET.get('oauth_token'),request.GET.get('oauth_verifier'))
    resp, content = GOOGLE_client.request(url, 'GET')
    if resp['status'] == '200':
        print 'OAuthGetAccessToken OK'
        db = init_db()
        curr_uid = get_session()['uid']
        curr_profile = db.query(profile).filter(profile.id==curr_uid).first()
        if curr_profile:
            curr_profile.g_oauth_token = urlparse.parse_qs(content)['oauth_token'][0]
            curr_profile.g_oauth_token_secret = urlparse.parse_qs(content)['oauth_token_secret'][0]
            curr_profile.save(session=db)
        bottle.redirect(url_root)
    else:
        print 'OAuthGetAccessToken status: %s' % resp['status']
        print content
        bottle.redirect(url_root)


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
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    isoauth = True if (curr_prof.g_oauth_token is not None and curr_prof.g_oauth_token_secret is not None) else False
    istoauth = True if (curr_prof.t_oauth_token is not None and curr_prof.t_oauth_token_secret is not None) else False
    return dict(items=objs,isoauth=isoauth,istoauth=istoauth)


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
    obj = db.query(campaign).filter(and_(campaign.profiles.any(id=sess['uid']),campaign.id==id)).first()
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
    obj = db.query(campaign).filter(and_(campaign.profiles.any(id=sess['uid']),campaign.id==id,campaign.uuid == request.POST.get('uuid'))).first()
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

@get(url_root+"/feedbacks")
@auth()
@view("all_custom_feedbacks")
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

@get(url_root_contacts+'/:cid/getemails')
@auth()
def handler(cid):
    db = init_db()
    g_oauth_token,g_oauth_token_secret,email = db.query(profile.g_oauth_token,profile.g_oauth_token_secret,profile.pemail).filter(profile.id==get_session()['uid']).first()
    if g_oauth_token is None:
        bottle.redirect(url_root+'/g/start_oauth')
    contact = db.query(profile).filter(profile.id==cid).first()
    last_email = db.query(chat).filter(and_(chat.profile_id==cid,chat.type==CHAT_EMAIL)).order_by(chat.ts).first()
    if not contact:
        bottle.redirect(url_root_contacts)
    if last_email:
        since = (datetime.datetime.fromtimestamp(last_email.ts)).strftime("%Y/%m/%d")
    else:
        since = "1970/01/01"
    token = oauth.Token(g_oauth_token,g_oauth_token_secret)
    conn = imaplib.IMAP4_SSL('imap.googlemail.com')
    conn.debug = 4
    try:
        conn.authenticate((GOOGLE_RESOURCE_URL % email), GOOGLE_consumer, token)
    except Exception as e:
        print e
        bottle.redirect(url_root+'/g/start_oauth')
    conn.select("INBOX",readonly=True)
    print "geting email for "+contact.pemail
    emails(conn,contact.pemail,since=since)
    bottle.redirect(url_root_contacts+'/%s/emails'%(cid))

@get(url_root_contacts + '/:cid/feedbacks')
@auth()
@view('all_feedbacks')
def handler(cid):
    db = init_db()
    item = db.query(profile).filter(profile.id == cid).first()

    return dict(items=item,cid=cid)
@get(url_root_contacts + '/:cid/feedbacks/new')
@auth()
@view('new_feedback')
def handler(cid):
    return dict(profile_id=cid, feedback_type=FEEDBACK_TYPE,status_type=status)
@post(url_root_contacts + '/:cid/feedbacks')
@auth()
def handle(cid):
    db = init_db()
    obj = feedback()
    prof = db.query(profile).filter(profile.id == cid).first()
    obj.update(request.POST,session=db)
    if prof:
        prof.feedbacks.append(obj)
        prof.save(session=db)

    bottle.redirect(url_root_contacts + '/' + cid + '/feedbacks/' + str(obj.id)) if obj else bottle.redirect(
        url_root_contacts)
@get(url_root_contacts + '/:cid/feedbacks/:id')
@auth()
@view("single_feedback")
def handler(cid, id):
    db = init_db()
    obj = db.query(feedback).filter(feedback.id == id).first()
    return dict(profile_id=cid, item=obj, feedback_type=FEEDBACK_TYPE,status_type=status)


@post(url_root_contacts + '/:cid/feedbacks/:id')
@auth()
def handler(cid, id):
    db = init_db()
    obj = db.query(feedback).filter(feedback.id == id).first()
    obj.update(request.POST,session=db)
    return bottle.redirect(url_root_contacts + '/%s/feedbacks/%s' % (cid, id))

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

@get(url_root_contacts+'/:cid/chats/:id/reply')
@auth()
@view("reply_chat")
def handler(cid,id):

    db = init_db()
    obj = db.query(chat).filter(chat.id==id).first()
    return dict(chat=obj)
@get(url_root_contacts+'/:cid/emails')
@auth()
@view("reply_email")
def handler(cid):

    db = init_db()
    obj =db.query(profile).filter(profile.id==cid).first()

    gtid = defaultdict(list)
    for x in obj.chats:
        js = json.loads(x.details)
        if 'gtid' in js:
            gtid[js['gtid']].append(x)
    return dict(chats=gtid)

@post(url_root_contacts+'/:cid/chats/:id/reply')
@auth()
def handler(cid,id):
    sess = get_session()
    db = init_db()
    current_profile = db.query(profile).filter(profile.id==sess['uid']).first()
    curr_chat = db.query(chat).filter(chat.id==id).first()
    reply = chat()
    reply.update(request.POST,session=db)
    curr_chat.replies.append(reply)
    curr_chat.save(session=db)
    reply.save(session=db)
    current_profile.chats.append(reply)
    current_profile.save(session=db)
    print reply.topic.content
    bottle.redirect(url_root_contacts+'/%s/chats/%s/reply' % (cid,id))




