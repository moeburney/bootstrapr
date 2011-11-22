import json
import bottle
from sqlalchemy.sql.expression import and_
from models import campaign
from models.campaign import init_db

__author__ = 'rohan'
from bottle import route, run, request, get, post
bottle.debug(True)

@get('/campaigns')
def handler():
    return json.dumps(init_db().query(campaign).all().order_by(campaign.startTs))


@post('/campaigns')
def handler():
    db = init_db()
    temp_camp = campaign(desc=request.POST("desc"),startTs=request.POST('sts'),endTs=request.POST("ets"),campaign_type=request.POST('ctype'))
    db.add(temp_camp)
    db.commit()
    return json.dumps(temp_camp)

@post('/campaigns/<ide:int>')
def handler():
    obj = json.loads(request.body)
    db = init_db()
    result = db.query(campaign).filter(and_(campaign.id==ide,campaign.uuid==obj['uuid']))
    if(result.count()<=0):
        bottle.redirect('/campaigns')
    

run(host='localhost', port=8080)