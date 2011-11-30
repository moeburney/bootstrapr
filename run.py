import argparse
import threading
import bottle
import Properties
from controller import app
from model import init_db, initwork

__author__ = 'rohan'
parser = argparse.ArgumentParser(description="Run Script for Marketing blasts")
parser.add_argument("-env", dest="env", action="store")
parser.add_argument("-p", dest="port", action="store")
parser.add_argument("--host", dest="host", action="store")
parser.add_argument("-s", dest="server", action="store")
args = parser.parse_args()

if("dev" in args.env):
    
    init_db()
    threading.Thread(target=initwork).start()
    print "### Running app in development environment"
    bottle.run(host='localhost', port=int(args.port), app=app)
if("prod" in args.env):
    
    init_db()
    threading.Thread(target=initwork).start()
    print "### Running app in production environment"
    bottle.run(host='localhost', port=int(args.port), app=app)
