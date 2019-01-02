#!/usr/bin/python3
# coding=utf-8


from flask import Flask, render_template, make_response
from mysql.connector import errorcode
import mysql.connector
from util import printError
from globalConfig import *
import datetime
import sys
import requests
import dhcpLeases

UPDATE_INTERVAL = 20		# Tiempo máximo que si no ha habido actualización, se declara como offline


SERVER_ADDRESS_LABEL = 'http://192.168.24.6:8080/rest/items/{0}'
SERVER_ADDRESS_STATE = 'http://192.168.24.6:8080/rest/items/{0}/state'

sondaTemp = {}
sondaHumedad = {}
sondaPresencia = {}

app = Flask(__name__)

def byebye(texto):
    printError(texto)
    printError("Shutting down the system as I can't start")
    sys.exit("Ooopss, I can't start. Check syslog.")
    
#
# Lee la configuracion de la tabla 'Configuracion'
#
def initConfiguration(conexion = None):
    if conexion == None:
        try:
            cnx = mysql.connector.connect(option_files="ohapp.cnf")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                byebye("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                byebye("Database does not exist")
            else:
                byebye(err)    
    else:
        cnx = conexion
        
    cursor = cnx.cursor()

    query = ("select * from Configuracion")
	
    cursor.execute(query)
#
# Inicializa las variables que contienen los nombres de todos los "items"
# de openHAB que hay que monitorizar o mostrar el resultado en el servidore Web
#
# sondaTemp         tiene todos los sensores tipo Temperatura
# sondaHumedad      tiene todos los sensores tipo Humedad
# sondaPresencia    tiene todos los sensores tipo Presencia
#
# Utilizo el método .encode('ascii') pues tal y como llega de la BBDD 
# no puedo utilizarlo directamente
#
    for sensor, tipo in cursor:
        sensor1 = sensor.encode('ascii')
        if tipo == 'temp':
            sondaTemp[sensor1] = {}
        elif tipo == 'humedad':
            sondaHumedad[sensor1] = {}
        elif tipo == 'presencia':
            sondaPresencia[sensor1] = {}

    cursor.close()
    
# Ahora toca la segunda parte
# encuentra la tabla donde se almacena la información
# de cada objeto

    cursor = cnx.cursor()

    query = ("SELECT * from Items")

    cursor.execute(query)

    for (Id, Name) in cursor:
        if Name in sondaTemp:
            sondaTemp[Name]['ID'] = 'Item' + str(Id)
        if Name in sondaHumedad:
            sondaHumedad[Name]['ID'] = 'Item' + str(Id)
   
    cursor.close()

    if conexion == "":
        cnx.close()
    return
    
def getHistorico():
    try:
        cnx = mysql.connector.connect(option_files="ohapp.cnf")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            printError("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            printError("Database does not exist")
        else:
            printError(err)

    cursor = cnx.cursor()

    query = ("select Dia, Media from Item1_Daily order by Dia desc limit 30")

    cursor.execute(query)

    listaFechas = []
    listaValores = []
    for (fecha, valor ) in cursor:

        listaFechas.append(fecha.strftime('%Y-%m-%d'))
        listaValores.append(float(valor))

    cursor.close()
    cnx.close()
    return listaFechas, listaValores

def getTemp(Sensor):
    try:
        cnx = mysql.connector.connect(option_files="ohapp.cnf")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
         printError("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            printError("Database does not exist")
        else:
            printError(err)

    cursor = cnx.cursor()

    query = ("select * from %s order by Time desc limit 1")

    cursor.execute(query, (Sensor, ))

    when = now = 0
    for (momento, valor ) in cursor:
        when = momento
        now = valor

    cursor.close()
    cnx.close()
    return valor

def getTempEx(Sensor):
    if 'ID' not in Sensor:
        return (datetime.datetime.now(), -99)

    try:
        cnx = mysql.connector.connect(option_files="ohapp.cnf")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
         printError("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            printError("Database does not exist")
        else:
            printError(err)

    cursor = cnx.cursor()

    query = ("select * from " + Sensor['ID'] + " order by Time desc limit 1")

    cursor.execute(query)

    when = now = 0
    for (momento, valor ) in cursor:
        when = momento
        now = valor

    cursor.close()
    cnx.close()
    return (momento, valor)

def getHumedadEx(Sensor):
    if 'ID' not in Sensor:
        return (datetime.datetime.now(), -99)

    try:
        cnx = mysql.connector.connect(option_files="ohapp.cnf")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
         printError("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            printError("Database does not exist")
        else:
            printError(err)

    cursor = cnx.cursor()

    query = ("select * from " + Sensor['ID'] + " order by Time desc limit 1")

    cursor.execute(query)

    when = now = 0
    for (momento, valor ) in cursor:
        when = momento
        now = valor

    cursor.close()
    cnx.close()
    return (momento, valor)

def updateTemps():
    now = datetime.datetime.now()
    for objeto in sondaTemp:
        sondaTemp[objeto]['Data'] = getTempEx(sondaTemp[objeto])
        sondaTemp[objeto]['Fecha'] = sondaTemp[objeto]['Data'][0].strftime("%d/%m/%Y %H:%M:%S")
        minutos = ((now - sondaTemp[objeto]['Data'][0]).seconds) / 60
        if minutos >= UPDATE_INTERVAL:
            sondaTemp[objeto]['Updated'] = 'OFF'
        else:
            sondaTemp[objeto]['Updated'] = 'ON'
    

def updateHumedad():
    for objeto in sondaHumedad:
        sondaHumedad[objeto]['Data'] = getHumedadEx(sondaHumedad[objeto])
        sondaHumedad[objeto]['Fecha'] = sondaHumedad[objeto]['Data'][0].strftime("%d/%m/%Y %H:%M:%S")


def getPresences():
    for objeto in sondaPresencia:
        url = SERVER_ADDRESS_LABEL.format(objeto)
        r = requests.get(url)
        if r.status_code == 200:
            respuesta = r.json()
            sondaPresencia[objeto]['Nombre'] = respuesta['label']
        url = SERVER_ADDRESS_STATE.format(objeto)
        r = requests.get(url)
        if r.status_code == 200:
            sondaPresencia[objeto]['Status'] = r.text
        else:
            sondaPresencia[objeto]['Status'] = "Desconocido"

def ordenarDhcpFijas(direccion):
    trozos = direccion["ip"].split('.')
    return (int(trozos[3]))
    
def getStaticDhcp():
    try:
        cnx = mysql.connector.connect(option_files="ohapp.cnf")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            printError("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            printError("Database does not exist")
        else:
            printError(err)
        
    cursor = cnx.cursor()

    query = ("select * from Dispositivos where Pool IN (1,2)")
	
    cursor.execute(query)
    
    direcciones = []

    for mac, ip, desc, ubicacion, pool, poolName in cursor:
        objeto = {}
        objeto['ip'] = ip
        objeto['ethernet'] = mac
        objeto['hostname'] = desc
        objeto['pool'] = poolName       #.encode('ascii')
        
        direcciones.append(objeto)
        
    direcciones.sort(key=ordenarDhcpFijas)
    cursor.close()
    cnx.close()
    return direcciones


@app.route("/presencia")
def presencia():
    getPresences()
    direcciones = dhcpLeases.getCurrentLeases()
    return render_template("redlocal.html", titulo = "Diseno Red", 
                            presencia = sondaPresencia, tabla = direcciones) 
    
        
@app.route("/temperatura")
def temp():
    updateTemps()
    updateHumedad()
    return render_template("temperatura.html", titulo = "Temperatura", 
                            temperatura = sondaTemp, humedad = sondaHumedad) 

@app.route("/red")
def showRed():
    getPresences()
    
    direcciones = dhcpLeases.getCurrentLeases1()

    return render_template("redlocal1.html", titulo = "Diseno Red", 
                            presencia = sondaPresencia, tabla = direcciones)     
#    direcciones = dhcpLeases.getCurrentLeases()
#    direccionesFijas = getStaticDhcp()
    
    
#    return render_template("redlocal.html", titulo = "Diseno Red", 
#                            presencia = sondaPresencia, tabla = direcciones, tablaFija = direccionesFijas) 


@app.route("/raspberry")
def showRaspBerry():
    updateTemps()

    return render_template("raspberry.html", titulo = "Diseno RaspBerry PI",
                            temperatura = sondaTemp) 

@app.route("/exterior")
def exterior():
    return render_template("exterior.html", titulo = "Exterior") 

@app.route("/")
def principal():
    return render_template("index.html", titulo = "Pagina Principal")

@app.route("/switch")
def swi():
    r = make_response(render_template('switch.html'))
    return r

@app.route("/historico")
def historico():
    vFechas, vValores = getHistorico()
    return render_template("historico.html", titulo = "Grafico Historico", fechas = vFechas, valores = vValores) 

    
#
# Comienzo del código
#

if len(sys.argv) == 2:
    opt_debug = True
else:
    opt_debug = False

initConfiguration()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = opt_debug)

"""
https://www.digitalocean.com/community/tutorials/how-to-set-up-basic-http-authentication-with-nginx-on-ubuntu-14-04
"""
