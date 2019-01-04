#! /usr/bin/python
# coding=utf-8

from mysql.connector import errorcode
import mysql.connector
import csv
import datetime
import sys
import syslog

def getYesterday():
    d = datetime.datetime.now() - datetime.timedelta(days=1)
    return(d.year, d.month, d.day)

def agregado(origen, destino):
    (year, month, day) = getYesterday()
    logDate = "{}-{}-{}".format(year,month,day)
    comienzo = "{}-{}-{} 00:00:00".format(year,month,day)
    final = "{}-{}-{} 23:59:59".format(year,month,day)
    cadena = "INSERT into " + destino + " (" + \
            """SELECT
              STR_TO_DATE(concat(date(Time),' ',HOUR(Time),':30:00'), '%Y-%m-%d %H:%i:%S') as 'Dia',
              HOUR(Time) as 'Inicio',
              HOUR(Time)+1 as 'Final',
              COUNT(*) as 'Muestras',
              round(avg(Value),2) as 'Media'
            FROM """ + origen + " "  
    cadena = cadena + """WHERE
              Time >= '""" + comienzo + "'" + \
            " AND Time <= '" + final + "'" + \
            """ GROUP BY 
              DATE(Time), 
              HOUR(Time)
            );"""
#    print("AGREGADO")
#    print(cadena)
#    print("Destino = "+destino)
#    print("Origen = "+origen)

#    return

    cursor1 = cnx.cursor()
    try:
        cursor1.execute(cadena)
        mensaje = "agregadoHoras: Tabla {0} Actualizada {1}".format(origen,logDate)
        syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_INFO, mensaje)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            mensaje = "agregadoHoras: ERROR: {0} Clave Duplicada {1}".format(origen,comienzo)
            syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_NOTICE, mensaje)
        else:
            mensaje = "agregadoHoras: Error Tabla {0} fecha {1} mensaje {2}".format(origen,comienzo,str(err))
            syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_ERR, mensaje)


    cnx.commit()
    cursor1.close()

def agregadoDiario(origen, destino):
    (year, month, day) = getYesterday()
    logDate = "{}-{}-{}".format(year,month,day)
    comienzo = "{}-{}-{} 00:00:00".format(year,month,day)
    final = "{}-{}-{} 23:59:59".format(year,month,day)
    cadena = "INSERT into " + destino + " (" + \
            """SELECT
              DATE(Time), count(*) as "Muestras",
              round(avg(Value),2) as "Media", min(Value) as "Minimo", max(Value) as "Maximo"
            FROM """ + origen + " "  
    cadena = cadena + """WHERE
              Time >= '""" + comienzo + "'" + \
            " AND Time <= '" + final + "'" + \
            """ GROUP BY 
              DATE(Time) 
            );"""
#    print("DIARIO")
#    print(cadena)
#    print("Destino = "+destino)
#    print("Origen = "+origen)

#    return

    cursor1 = cnx.cursor()
    try:
        cursor1.execute(cadena)
        mensaje = "agregadoDiario: Tabla {0} Actualizada {1}".format(origen,logDate)
        syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_INFO, mensaje)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            mensaje = "agregadoDiario: ERROR: {0} Clave Duplicada {1}".format(origen,comienzo)
            syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_NOTICE, mensaje)
        else:
            mensaje = "agregadoDiario: Error Tabla {0} fecha {1} mensaje {2}".format(origen,comienzo,str(err))
            syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_ERR, mensaje)


    cnx.commit()
    cursor1.close()
#
# Comienzo
#

syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_INFO, "agregadoDiario: EMPEZANDO")

try:
    cnx = mysql.connector.connect(option_files="/home/openhabian/backup/myopc.cnf")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_ERR, "Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_ERR, "Database does not exist")
    else:
        syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_ERR, err)

cursor = cnx.cursor()

query = "show tables"
cursor.execute(query)
lista = []
listaDiaria = []
for (Name,) in cursor:
    if "Hourly" in Name:
        elemento = []
        posicion = Name.find('_')
        tablaOrigen = Name[0:posicion]
        elemento.append(tablaOrigen)
        elemento.append(Name)
        lista.append(elemento)
    if "Daily" in Name:
        elemento = []
        posicion = Name.find('_')
        tablaOrigen = Name[0:posicion]
        elemento.append(tablaOrigen)
        elemento.append(Name)
        listaDiaria.append(elemento)
        
cursor.close()

for (origen, destino) in lista:
    agregado(origen, destino)

for (origen, destino) in listaDiaria:
    agregadoDiario(origen, destino)

cnx.close()

syslog.syslog(syslog.LOG_LOCAL7 | syslog.LOG_INFO, "agregadoDiario: TERMINANDO")
