import argparse
from subprocess import call
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
    call("uwsgi -s 127.0.0.1:8080 -w controller --callable app -p 4 -M -t 20 --limit-as 200 -m -T ",shell=True)
    #bottle.run(host='localhost', port=int(args.port), app=app)
if("prod" in args.env):
    
    init_db()
    threading.Thread(target=initwork).start()
    print "### Running app in production environment"
    call("uwsgi -s 127.0.0.1:8080 -w controller --callable app  -p 4 -M -t 20 --limit-as 200 -m -T ",shell=True)
    #bottle.run(host='localhost', port=int(args.port), app=app)
