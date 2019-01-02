# coding=utf-8
import syslog
import inspect
from globalConfig import *

def printError(errText):
# python 3
# print(inspect.stack()[1].function)
    syslog.syslog(syslog.LOG_ERR | syslog.LOG_USER, "ERROR: " + inspect.stack()[1][3] + " Module: " + errText)
    if opt_debug:
        print("ERROR: " + inspect.stack()[1][3] + " Module: " + errText)

