pythoninterpretor=/usr/bin/python2
export OURAPP=`pwd`
export PYTHONPATH=$PYTHONPATH:.:$OURAPP:$OURAPP/src/
$pythoninterpretor ./run.py $*