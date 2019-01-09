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

# 
# select count(*) from Item1_Hourly where date(Dia) = current_date()-1;
#
def isUpdatedTable(nombreTabla):
    cnx = openDDBB()

    cursor = cnx.cursor()
    tabla1 = nombreTabla + "_Hourly"
    tabla2 = nombreTabla + "_Daily"
    comando1 = "select count(*) from {} where date(Dia) = current_date()-1".format(tabla1)
    comando2 = "select count(*) from {} where date(Dia) = current_date()-1".format(tabla2)

    try:
        cursor.execute(comando1)
        for (resultado,) in cursor:
            nResultado1 = int(resultado)

    except mysql.connector.Error as err:
        printError("Error while accessing table {}".format(tabla1))
        printError(str(err))
        nResultado1 = 0

    try:
        cursor.execute(comando2)
        for (resultado,) in cursor:
            nResultado2 = int(resultado)
    except mysql.connector.Error as err:
        printError("Error while accessing table {}".format(tabla2))
        printError(str(err))
        nResultado2 = 0

    cursor.close()
    closeDDBB(cnx)
    return False if nResultado1 == 0 or nResultado2 == 0 else True

def getLatestData(tabla):
    """
    Obtiene la información de la base de datos de la tabla especificada
    como parámetro.
    La tabla debe ser la que contiene la información de todas las muestras
    de los sensores, no la diaria, ni la mensual.
    """
    cnx = openDDBB()
    
    cursor = cnx.cursor()

    """ 672 """

    texto = ("select Time, Value from {} order by Time desc limit 672".format(tabla))

    cursor.execute(texto)

    listaFechas = []
    listaValores = []
    for (fecha, valor ) in cursor:

        listaFechas.append(fecha.strftime('%Y-%m-%d %H:%M'))
        listaValores.append(float(valor))

    cursor.close()
    closeDDBB(cnx)
    return listaFechas, listaValores
