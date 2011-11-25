import json
from beaker.middleware import SessionMiddleware
import bottle
from models.campaign import get_all, get_one, campaign_type_get_all, campaign, gaintypes, expensetypes, status


ENV =['Production','Development']

__author__ = 'rohan'
from bottle import route, run, request, get, post,view
bottle.debug(True)

session_opts = {
    'session.auto':True,
    'session.timeout' : 180,
    'session.type': 'ext:database',
    'session.url': 'mysql://rohan:gotohome@localhost/ron',
    'session.key':'campaignsession',
    'session.secret' : 'gotohome',
    'session.lock_dir':'./'
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
            return bottle.redirect('/campaigns/login.html')
        print "after handle"
        return wrapper
    return decorator
def logout():
    get_session().delete()
def login(user,passwd):
    if user=='rohan' and passwd=='gotohome':
        get_session()['user']=user
        get_session()['loggedin'] = True
    else:
        get_session().delete()
@post('/campaigns/login')
def handler():
    login(request.POST.get('user'),request.POST.get('passwd'))
    if not validate_login():
        bottle.redirect('/campaigns/login.html?err=invalid')
    bottle.redirect('/campaigns')
@get('/campaigns/logout')
def handler():
    logout()
    bottle.redirect('/campaigns')
@get('/campaigns')
@view('all_campaigns')
#@auth()
def handler():
    get_session()['ip'] = request.environ['REMOTE_ADDR']
    objs = get_all()
    print "last ip --> "+get_session()['ip']
    try:
        print "last id "+get_session()['id']
    except KeyError as e:
        pass
    return dict(items = objs)

@get('/campaigns/:id')
#@auth()
@view('single_campaign')
def handler(id):
    obj = get_one(id)
    if(obj is None):
        bottle.redirect('/campaigns')
    s = get_session()
    s['id'] = id
    print obj.desc
    types = campaign_type_get_all(exclude=obj.campaign_type)

    return dict(item=obj,ctypes=types,uattrs=json.loads(obj.attrs),gains=gaintypes,expenses=expensetypes,status=status,ugains=json.loads(obj.gains),uexpenses=json.loads(obj.expenses))

@get('/campaigns/:id/destroy')
#@auth()
def handler(id):
    obj = get_one(id)
    if(obj is None):
        bottle.redirect("/campaigns")
    obj.delete()
    bottle.redirect('/campaigns')

@get('/campaigns/new')
#@auth()
@view('new_campaign')
def handler():
    return dict(ctypes=campaign_type_get_all(),gains=gaintypes,expenses=expensetypes,status=status)
@post('/campaigns')
#@auth()
def handler():
    obj = campaign()
    obj.update(request.POST)
    if(obj is None):
        return "error"
    bottle.redirect('/campaigns/'+str(obj.id))

@post('/campaigns/:id')
#@auth()
def handler(id):
    obj = get_one(id,uuid=request.POST.get("uuid"))
    if(obj is None):
        bottle.redirect('/campaigns')
    obj.update(request.POST)
    print "after bk "+obj.desc
    bottle.redirect('/campaigns/'+id)
    
