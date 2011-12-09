from _collections import defaultdict
import os
import datetime
import string
import threading
import oauth2.clients.imap as imaplib
import json
import urllib
import urlparse
from beaker.middleware import SessionMiddleware
import bottle
from sqlalchemy.sql.expression import and_, desc
from bottle import route, request, get, post, view
from Properties import TWITTER_REQUEST_TOKEN_URL, TWITTER_CALLBACK_URL, TWITTER_AUTHORIZATION_URL, TWITTER_ACCESS_TOKEN_URL, GOOGLE_REQUEST_TOKEN_URL, GOOGLE_SCOPE, GOOGLE_CALLBACK_URL, GOOGLE_AUTHORIZATION_URL, GOOGLE_ACCESS_TOKEN_URL, GOOGLE_RESOURCE_URL

from model import campaign, status, expensetypes, gaintypes, campaign_type_get_all, status_profile, init_db, profile, chat, chat_type, profile_types, emails, CHAT_EMAIL, FEEDBACK_TYPE, feedback, tweet,  TWITTER_consumer,   TWITTER_client,    GOOGLE_xoauth_displayname, GOOGLE_consumer,   GOOGLE_client, get_campaign_timeline, get_campaign_data_point, get_contact_timeline, PROFILE_OWNER
import oauth2 as oauth
__author__ = 'rohan'
os.chdir(os.path.dirname(__file__))

url_root = "/campaigns"
ENV = ['Production', 'Development']

__author__ = 'rohan'

bottle.debug()

bottle.TEMPLATE_PATH.insert(0,'./static')





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
        if session['loggedin']:
            return True
    else:
        return False


def auth(check_func=validate_login):
    def decorator(view):
        def wrapper(*args, **kwargs):
            auth = check_func()
            if auth:
                return view(*args, **kwargs)
            return bottle.redirect('/login.html')


        return wrapper

    return decorator


def logout():
    sess = get_session()
    sess.delete()


def login(user, passwd):
    db = init_db()
    user = db.query(profile).filter(and_(profile.name==user,profile.passwd==passwd)).first()
    if user:
        sess = get_session()
        sess['uid'] = user.id
        sess['loggedin'] = True
        db.close()
    else:
        db.close()
        return

@get(url_root+'/t/start_oauth')
def handler():
    global TWITTER_client
    url = TWITTER_REQUEST_TOKEN_URL+'?oauth_callback=%s' % TWITTER_CALLBACK_URL
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
    resp, content = TWITTER_client.request(url)
    if resp['status'] == '200':
        print 'OAuthGetAccessToken OK'
        db = init_db()
        try:
            sess = get_session()
            curr_uid = sess['uid']
        except :
            db.close()
            bottle.redirect(url_root)
        curr_profile = db.query(profile).filter(profile.id==curr_uid).first()
        if curr_profile:
            curr_profile.t_oauth_token = urlparse.parse_qs(content)['oauth_token'][0]
            curr_profile.t_oauth_token_secret = urlparse.parse_qs(content)['oauth_token_secret'][0]
            curr_profile.problem=""
            curr_profile.save(session=db)
        db.close()
        bottle.redirect(url_root)
    else:
        db.close()
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
    resp, content = GOOGLE_client.request(url)
    if resp['status'] == '200':
        print 'OAuthGetAccessToken OK'
        db = init_db()
        try:
            sess = get_session()
            curr_uid = sess['uid']
        except :
            db.close()
            bottle.redirect(url_root)
        curr_profile = db.query(profile).filter(profile.id==curr_uid).first()
        if curr_profile:
            curr_profile.g_oauth_token = urlparse.parse_qs(content)['oauth_token'][0]
            curr_profile.g_oauth_token_secret = urlparse.parse_qs(content)['oauth_token_secret'][0]
            curr_profile.save(session=db)
        db.close()
        bottle.redirect(url_root)
    else:
        db.close()
        print 'OAuthGetAccessToken status: %s' % resp['status']
        print content
        bottle.redirect(url_root)


@post(url_root + '/login')
def handler():
    login(request.POST.get('user'), request.POST.get('passwd'))
    if not validate_login():
        bottle.redirect('/login.html?err=invalid')
    bottle.redirect(url_root)


@get(url_root + '/logout')
def handler():
    logout()
    bottle.redirect(url_root)


@get(url_root)
@view('index')
@auth()
def handler():
    db = init_db()
    sess = get_session()
    objs = db.query(campaign).filter(campaign.profiles.any(id=sess['uid'])).all()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    isoauth = True if (curr_prof.g_oauth_token is not None and curr_prof.g_oauth_token_secret is not None) else False
    istoauth = True if (curr_prof.t_oauth_token is not None and curr_prof.t_oauth_token_secret is not None) else False
    istoauth = False if curr_prof.problem != "" else istoauth
    db.close()
    return dict(items=objs,isoauth=isoauth,istoauth=istoauth,profile=curr_prof,sess=sess)


@get(url_root + '/:id')
@auth()
@view('single_campaign')
def handler(id):
    sess = get_session()
    db = init_db()
    obj = db.query(campaign).filter(and_(campaign.profiles.any(id=sess['uid']),campaign.id==id)).first()
    if(obj is None):
        db.close()
        bottle.redirect(url_root)

    types = campaign_type_get_all(exclude=obj.campaign_type)
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(item=obj, ctypes=types, uattrs=json.loads(obj.attrs), gains=gaintypes, expenses=expensetypes,
                status=status, ugains=json.loads(obj.gains), uexpenses=json.loads(obj.expenses),profile=curr_prof)

@get(url_root+'/:id/timeline')
@auth()
def handler(id):
    sess = get_session()
    timeline = get_campaign_timeline(id,uid=sess['uid'])
    print json.dumps(timeline)
    return json.dumps(timeline)
@get(url_root+'/:id/:ts/data')
@auth()
def handler(id,ts):
    sess = get_session()
    data = get_campaign_data_point(id,sess['uid'],ts)
    print json.dumps(data)
    return json.dumps(data)
@get(url_root + '/:id/destroy')
@auth()
def handler(id):
    sess = get_session()
    db = init_db()
    obj = db.query(campaign).filter(and_(campaign.profiles.any(id=sess['uid']),campaign.id==id)).first()
    if obj is None:
        bottle.redirect(url_root)
    todelete =[]
    for p in obj.profiles:
        print "\n\nremoving "+p.name +" from campaign "+obj.desc
        todelete.append(p)
    del obj.profiles
    db.commit()
    db.delete(obj)
    db.commit()
    for t in todelete:
        if t.profile_type != PROFILE_OWNER:
            db.delete(t)
            db.commit()
    db.close()
    bottle.redirect(url_root)


@get(url_root + '/new')
@auth()
@view('new_campaign')
def handler():
    db = init_db()
    sess = get_session()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(ctypes=campaign_type_get_all(), gains=gaintypes, expenses=expensetypes, status=status,profile=curr_prof)


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
    
    if obj is None:
        db.close()
        return "error"
    db.close()
    bottle.redirect(url_root)


@post(url_root + '/:id')
@auth()
def handler(id):
    db = init_db()
    sess = get_session()
    obj = db.query(campaign).filter(and_(campaign.profiles.any(id=sess['uid']),campaign.id==id,campaign.uuid == request.POST.get('uuid'))).first()
    if obj is None:
        db.close()
        bottle.redirect(url_root)
    obj.update(request.POST,session=db)
    db.close()
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
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    collect = []
    for x in objs:
        collect.extend(x.profiles)
    db.close()
    return dict(items=collect,profile=curr_prof)

@get(url_root+"/feedbacks")
@auth()
@view("all_custom_feedbacks")
def handler():
    sess = get_session()
    db = init_db()
    objs = db.query(campaign).filter(campaign.profiles.any(id=sess['uid'])).all()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    profs = []
    for camp in objs:
        for prof in camp.profiles:
            profs.append(prof)
    db.close()
    return dict(items=profs,profile=curr_prof)

@get(url_root_contacts + "/new")
@view("new_contact")
@auth()
def handler():
    db = init_db()
    sess = get_session()
    campaigns = db.query(campaign.id,campaign.desc).filter(campaign.profiles.any(id=sess['uid'])).all()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(pstatuses=status_profile, campaigns=campaigns,type=profile_types.index(request.params.get('type') if 'type' in request.params else 'contact'),profile=curr_prof)


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
    db.close()
    bottle.redirect(url_root_contacts)


@get(url_root_contacts + "/:cid")
@auth()
@view('single_contact')
def handler(cid):
    db = init_db()
    obj = db.query(profile).filter(profile.id == cid).first()
    sess = get_session()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    isoauth = True if (curr_prof.g_oauth_token is not None and curr_prof.g_oauth_token_secret is not None) else False
    istoauth = True if (curr_prof.t_oauth_token is not None and curr_prof.t_oauth_token_secret is not None) else False
    istoauth = False if curr_prof.problem != "" else istoauth
    return dict(obj=obj,campaign=obj.campaign,pstatuses=status_profile,profile=curr_prof,isoauth=isoauth,istoauth=istoauth) if obj else bottle.redirect(
        url_root_contacts)
@get(url_root_contacts + "/:cid/showtimeline")
@auth()
@view('single_contact_timeline')
def handler(cid):
    db = init_db()
    obj = db.query(profile).filter(profile.id == cid).first()
    sess = get_session()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    isoauth = True if (curr_prof.g_oauth_token is not None and curr_prof.g_oauth_token_secret is not None) else False
    istoauth = True if (curr_prof.t_oauth_token is not None and curr_prof.t_oauth_token_secret is not None) else False
    istoauth = False if curr_prof.problem != "" else istoauth
    db.close()
    return dict(obj=obj,campaign=obj.campaign,pstatuses=status_profile,profile=curr_prof,isoauth=isoauth,istoauth=istoauth) if obj else bottle.redirect(
        url_root_contacts)

@get(url_root_contacts + "/:cid/timeline/:type")
@auth()
def handler(cid,type):
    if type in ["email","chat","twitter","feedback"]:
        timeline = get_contact_timeline(cid,type)
        if timeline:
            print json.dumps(timeline)
            return json.dumps(timeline)
    else:
        bottle.redirect(url_root_contacts+"/%s" % cid)
@post(url_root_contacts + "/:cid")
@auth()
def handler(cid):
    db = init_db()
    obj = db.query(profile).filter(and_(profile.id == cid, profile.uuid == request.POST.get('uuid'))).first()
    if obj is None:
        db.close()
        bottle.redirect(url_root_contacts)
    obj.update(request.POST,session=db)
    db.close()
    bottle.redirect(url_root_contacts + '/' + cid)

@get(url_root_contacts+'/:cid/getemails')
@auth()
def handler(cid):
    db = init_db()
    sess = get_session()
    g_oauth_token,g_oauth_token_secret,email = db.query(profile.g_oauth_token,profile.g_oauth_token_secret,profile.pemail).filter(profile.id==sess['uid']).first()
    if g_oauth_token is None:
        db.close()
        bottle.redirect(url_root+'/g/start_oauth')
    contact = db.query(profile).filter(profile.id==cid).first()
    last_email = db.query(chat).filter(and_(chat.profile_id==cid,chat.type==CHAT_EMAIL)).order_by(chat.ts).first()
    if not contact:
        db.close()
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
        db.close()
        bottle.redirect(url_root+'/g/start_oauth')
    conn.select("INBOX",readonly=True)
    print "geting email for "+contact.pemail
    threading.Thread(target=emails,args=(conn,contact.pemail,since)).start()
    sess = get_session()
    sess['msg'] = "Emails for %s will be fetched in a few milliseconds" % contact.pemail
    sess['msg-old'] = False
    db.close()
    bottle.redirect(url_root_contacts+'/%s/emails' % cid)

@get(url_root_contacts+'/:cid/tweets')
@auth()
@view("reply_tweets")
def handler(cid):
    db = init_db()
    sess = get_session()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()

    contact_profile = db.query(profile).filter(profile.id==cid).first()
    print "Mentioned "+str(curr_prof.twitter)+" mentioner "+str(contact_profile.twitter)
    tweets = db.query(tweet).filter(and_(tweet.mentioned==curr_prof.twitter,tweet.mentioner==contact_profile.twitter)).order_by(desc(tweet.ts))
    db.close()
    return dict(items=tweets,profile=curr_prof,contact=contact_profile)
@get(url_root_contacts + '/:cid/feedbacks')
@auth()
@view('all_feedbacks')
def handler(cid):
    db = init_db()
    item = db.query(profile).filter(profile.id == cid).first()
    sess = get_session()

    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(items=item,cid=cid,profile=curr_prof)
@get(url_root_contacts + '/:cid/feedbacks/new')
@auth()
@view('new_feedback')
def handler(cid):
    db = init_db()
    sess = get_session()
    contact = db.query(profile).filter(profile.id==cid).first()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(profile_id=cid, feedback_type=FEEDBACK_TYPE,status_type=status,profile=curr_prof,contact=contact)
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
    db.close()
    bottle.redirect(url_root+ '/feedbacks') if obj else bottle.redirect(
        url_root_contacts)
@get(url_root_contacts + '/:cid/feedbacks/:id')
@auth()
@view("single_feedback")
def handler(cid, id):
    db = init_db()
    obj = db.query(feedback).filter(feedback.id == id).first()
    item = db.query(profile).filter(profile.id == cid).first()
    sess = get_session()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(profile_id=cid, item=obj, feedback_type=FEEDBACK_TYPE,status_type=status,profile=curr_prof,contact=item)


@post(url_root_contacts + '/:cid/feedbacks/:id')
@auth()
def handler(cid, id):
    db = init_db()
    obj = db.query(feedback).filter(feedback.id == id).first()
    obj.update(request.POST,session=db)
    db.close()
    return bottle.redirect(url_root_contacts + '/%s/feedbacks/%s' % (cid, id))

@get(url_root_contacts + '/:cid/chats')
@auth()
@view('all_chats')
def handler(cid):
    db = init_db()
    item = db.query(profile).filter(profile.id == cid).first()
    sess = get_session()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(items=item,cid=cid,profile=curr_prof,contact=item)


@get(url_root_contacts + '/:cid/chats/new')
@auth()
@view('new_chat')
def handler(cid):
    db = init_db()
    item = db.query(profile).filter(profile.id == cid).first()
    sess = get_session()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(profile_id=cid, chat_type=chat_type,contact=item,profile=curr_prof)


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
    db.close()
    bottle.redirect(url_root_contacts + '/' + cid + '/chats/' + str(obj.id)) if obj else bottle.redirect(
        url_root_contacts)
@get(url_root_contacts + '/:cid/chats/:id')
@auth()
@view("single_chat")
def handler(cid, id):
    db = init_db()
    obj = db.query(chat).filter(chat.id == id).first()
    item = db.query(profile).filter(profile.id == cid).first()
    sess = get_session()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(profile_id=cid, item=obj, chat_type=chat_type,contact=item,profile=curr_prof)


@post(url_root_contacts + '/:cid/chats/:id')
@auth()
def handler(cid, id):
    db = init_db()
    obj = db.query(chat).filter(chat.id == id).first()
    obj.update(request.POST,session=db)
    db.close()
    return bottle.redirect(url_root_contacts + '/%s/chats/%s' % (cid, id))

@get(url_root_contacts+'/:cid/chats/:id/reply')
@auth()
@view("reply_chat")
def handler(cid,id):

    db = init_db()
    obj = db.query(chat).filter(chat.id==id).first()
    item = db.query(profile).filter(profile.id == cid).first()
    sess = get_session()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(chat=obj,contact=item,profile=curr_prof)
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
    item = db.query(profile).filter(profile.id == cid).first()
    sess = get_session()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    db.close()
    return dict(chats=gtid,contact=item,profile=curr_prof,sess=sess)

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
    print reply.replies.topic.content
    db.close()
    bottle.redirect(url_root_contacts+'/%s/chats/%s/reply' % (cid,id))

@get(url_root+"/feedbacks/new")
@auth()
@view("new_custom_feedback")
def handler():
    sess = get_session()
    db = init_db()
    curr_prof = db.query(profile).filter(profile.id==sess['uid']).first()
    all_campaigns =  db.query(campaign).filter(campaign.profiles.any(id=sess['uid'])).all()
    profiles = []
    for obj in all_campaigns:
        profiles.extend(obj.profiles)
    db.close()
    return dict(contacts=profiles,profile=curr_prof,feedback_type=FEEDBACK_TYPE,status_type=status)
