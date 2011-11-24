import argparse
import sys
from controllers.campaign import app
import bottle

__author__ = 'rohan'
import os, sys
cmd_folder = os.path.dirname(os.path.abspath(__file__))
if cmd_folder not in sys.path:
     sys.path.insert(0, cmd_folder)
parser= argparse.ArgumentParser(description="Run Script for Marketing blasts")
parser.add_argument("-env",dest="env",action="store")
parser.add_argument("-p",dest="port",action="store")
parser.add_argument("-h",dest="host",action="store")
parser.add_argument("-s",dest="server",action="store")
args = parser.parse_args()
if("dev" in env):
    print "### Running app in development environment"
    bottle.run(host='localhost', port=int(args.port),app=app)
if("prod" in env):
    print "### Running app in production environment"
    bottle.run(host='localhost', port=int(args.port),app=app,server=args.server)
