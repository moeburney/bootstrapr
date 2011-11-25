import argparse
import bottle
from controller import app

__author__ = 'rohan'
parser= argparse.ArgumentParser(description="Run Script for Marketing blasts")
parser.add_argument("-env",dest="env",action="store")
parser.add_argument("-p",dest="port",action="store")
parser.add_argument("--host",dest="host",action="store")
parser.add_argument("-s",dest="server",action="store")
args = parser.parse_args()
if("dev" in args.env):
    print "### Running app in development environment"
    bottle.run(host='localhost', port=int(args.port),app=app)
if("prod" in args.env):
    print "### Running app in production environment"
    bottle.run(host='localhost', port=int(args.port),app=app,server=args.server)
