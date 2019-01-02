# coding=utf-8

# Desactivo error de modulo no encontrado al no estar
# disponible para Windows
# pylint: disable=E0401
import syslog
# pylint: enable=E0401
import inspect
import settings
import mysql.connector


def printError(errText):
# python 3
# print(inspect.stack()[1].function)
    syslog.syslog(syslog.LOG_ERR | syslog.LOG_USER, "ERROR: " + inspect.stack()[1][3] + " Module: " + errText)
    if settings.opt_debug:
        print("ERROR: " + inspect.stack()[1][3] + " Module: " + errText)


def openDDBB():
    try:
        cnx = mysql.connector.connect(option_files="ohapp.cnf")
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            printError("Something is wrong with your user name or password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            printError("Database does not exist")
        else:
            printError(err)
    return cnx

def closeDDBB(connection):
    connection.close()