import json
import bottle
from sqlalchemy.sql.expression import and_
from models import campaign
from models.campaign import init_db, get_all, get_one, campaign_type_get_all, campaign

__author__ = 'rohan'
from bottle import route, run, request, get, post,view
bottle.debug(True)
@get('/campaigns')
@view('all_campaigns')
def handler():
    objs = get_all()
    return dict(items = objs)

@get('/campaigns/:ide')
@view('single_campaign')
def handler(ide):
    obj = get_one(ide)
    if(obj is None):
        bottle.redirect('/')
    print obj.desc
    types = campaign_type_get_all(exclude=obj.campaign_type)
    return dict(item=obj,attrs=json.loads(obj.attrs),ctypes=types,uattrs=json.loads(obj.attrs))

@post('/campaigns')
def handler():
    obj = campaign()
    obj.update(request.POST)
    if(obj is None):
        return "error"
    bottle.redirect('/campaigns/'+str(obj.id))

@post('/campaigns/:ide')
def handler(ide):
    obj = get_one(ide,uuid=request.POST.get("uuid"))
    if(obj is None):
        bottle.redirect('/campaigns')
    obj.update(request.POST)
    print "after bk "+obj.desc
    bottle.redirect('/campaigns/'+ide)
    
run(host='localhost', port=8080)