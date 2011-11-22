import json
import bottle
from sqlalchemy.sql.expression import and_
from models import campaign
from models.campaign import init_db, get_all, get_one, campaign_type_get_all, campaign_type_get_one

__author__ = 'rohan'
from bottle import route, run, request, get, post,view
bottle.debug(True)
@get('/campaigns')
def handler():
    db = init_db()
    objs = get_all()
    return objs[0].desc

@get('/campaigns/:ide')
@view('single_campaign')
def handler(ide):
    obj = get_one(ide)
    if(obj is None):
        bottle.redirect('/')
    print obj.desc
    main_campaign_type = campaign_type_get_one(obj.campaign_type)
    types = campaign_type_get_all(exclude=obj.campaign_type)
    attrs = json.loads(obj.attrs)
    return dict(item=obj,attrs=json.loads(obj.attrs),ctypes=types,main_ctype=main_campaign_type,uattrs=attrs)

@post('/campaigns')
def handler():
    db = init_db()
    temp_camp = campaign(desc=request.POST("desc"),startTs=request.POST('sts'),endTs=request.POST("ets"),campaign_type=request.POST('ctype'))
    db.add(temp_camp)
    db.commit()
    bottle.redirect('/campaigns/'+temp_camp.id)

@post('/campaigns/:ide')
def handler(ide):
    obj = get_one(ide,uuid=request.POST.get("uuid"))
    if(obj is None):
        bottle.redirect('/campaigns')
    obj.update(request.POST)
    print "after bk "+obj.desc
    bottle.redirect('/campaigns/'+ide)
    
run(host='localhost', port=8080)