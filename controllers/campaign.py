import json
import bottle
from models.campaign import get_all, get_one, campaign_type_get_all, campaign

__author__ = 'rohan'
from bottle import route, run, request, get, post,view
bottle.debug(True)
@get('/campaigns')
@view('all_campaigns')
def handler():
    objs = get_all()
    return dict(items = objs)

@get('/campaigns/:id')
@view('single_campaign')
def handler(id):
    obj = get_one(id)
    if(obj is None):
        bottle.redirect('/campaigns')
    print obj.desc
    types = campaign_type_get_all(exclude=obj.campaign_type)
    return dict(item=obj,attrs=json.loads(obj.attrs),ctypes=types,uattrs=json.loads(obj.attrs))

@get('/campaigns/:id/destroy')
def handler(id):
    obj = get_one(id)
    if(obj is None):
        bottle.redirect("/campaigns")
    obj.delete()
    bottle.redirect('/campaigns')
@post('/campaigns')
def handler():
    obj = campaign()
    obj.update(request.POST)
    if(obj is None):
        return "error"
    bottle.redirect('/campaigns/'+str(obj.id))

@post('/campaigns/:id')
def handler(id):
    obj = get_one(id,uuid=request.POST.get("uuid"))
    if(obj is None):
        bottle.redirect('/campaigns')
    obj.update(request.POST)
    print "after bk "+obj.desc
    bottle.redirect('/campaigns/'+id)
    
run(host='localhost', port=8080)