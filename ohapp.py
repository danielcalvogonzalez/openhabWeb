#!/usr/bin/python3
# coding=utf-8

from flask import Flask, render_template, make_response
from mysql.connector import errorcode
import mysql.connector
import settings
import datetime
import sys
import requests

import util
import dhcpLeases


app = Flask(__name__)

def byebye(texto):
    util.printError(texto)
    util.printError("Shutting down the system as I can't start")
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
#
    for sensor, tipo in cursor:
        if tipo == 'temp':
            settings.sondaTemp[sensor] = {}
        elif tipo == 'humedad':
            settings.sondaHumedad[sensor] = {}
        elif tipo == 'presencia':
            settings.sondaPresencia[sensor] = {}
    
# Ahora toca la segunda parte
# encuentra la tabla donde se almacena la información
# de cada objeto

    query = ("SELECT * from Items")

    cursor.execute(query)

    for (Id, Name) in cursor:
        if Name in settings.sondaTemp:
            settings.sondaTemp[Name]['ID'] = 'Item' + str(Id)
        if Name in settings.sondaHumedad:
            settings.sondaHumedad[Name]['ID'] = 'Item' + str(Id)
   
    cursor.close()

    if conexion == "":
        cnx.close()
    return
    
def getHistorico():
    cnx = util.openDDBB()
    
    cursor = cnx.cursor()

    query = ("select Dia, Media from Item1_Daily order by Dia desc limit 30")

    cursor.execute(query)

    listaFechas = []
    listaValores = []
    for (fecha, valor ) in cursor:

        listaFechas.append(fecha.strftime('%Y-%m-%d'))
        listaValores.append(float(valor))

    cursor.close()
    util.closeDDBB(cnx)
    return listaFechas, listaValores

def getTemp(Sensor):
    cnx = util.openDDBB()

    cursor = cnx.cursor()

    query = ("select * from %s order by Time desc limit 1")

    cursor.execute(query, (Sensor, ))

    when = now = 0
    for (momento, valor ) in cursor:
        when = momento
        now = valor

    cursor.close()
    util.closeDDBB(cnx)
    return valor

def getTempEx(Sensor):
    if 'ID' not in Sensor:
        return (datetime.datetime.now(), -99)

    cnx = util.openDDBB()

    cursor = cnx.cursor()

    query = ("select * from " + Sensor['ID'] + " order by Time desc limit 1")

    cursor.execute(query)

    when = now = 0
    for (momento, valor ) in cursor:
        when = momento
        now = valor

    cursor.close()
    
    util.closeDDBB(cnx)
    
    return (momento, valor)

def getHumedadEx(Sensor):
    if 'ID' not in Sensor:
        return (datetime.datetime.now(), -99)

    cnx = util.openDDBB()

    cursor = cnx.cursor()

    query = ("select * from " + Sensor['ID'] + " order by Time desc limit 1")

    cursor.execute(query)

    when = now = 0
    for (momento, valor ) in cursor:
        when = momento
        now = valor

    cursor.close()
    util.closeDDBB(cnx)
    return (momento, valor)

def updateTemps():
    now = datetime.datetime.now()
    for objeto in settings.sondaTemp:
        settings.sondaTemp[objeto]['Data'] = getTempEx(settings.sondaTemp[objeto])
        settings.sondaTemp[objeto]['Fecha'] = settings.sondaTemp[objeto]['Data'][0].strftime("%d/%m/%Y %H:%M:%S")
        minutos = ((now - settings.sondaTemp[objeto]['Data'][0]).seconds) / 60
        if minutos >= settings.UPDATE_INTERVAL:
            settings.sondaTemp[objeto]['Updated'] = 'OFF'
        else:
            settings.sondaTemp[objeto]['Updated'] = 'ON'
    

def updateHumedad():
    for objeto in settings.sondaHumedad:
        settings.sondaHumedad[objeto]['Data'] = getHumedadEx(settings.sondaHumedad[objeto])
        settings.sondaHumedad[objeto]['Fecha'] = settings.sondaHumedad[objeto]['Data'][0].strftime("%d/%m/%Y %H:%M:%S")


def getPresences():
    for objeto in settings.sondaPresencia:
        url = settings.SERVER_ADDRESS_LABEL.format(objeto)
        r = requests.get(url)
        if r.status_code == 200:
            respuesta = r.json()
            settings.sondaPresencia[objeto]['Nombre'] = respuesta['label']
        url = settings.SERVER_ADDRESS_STATE.format(objeto)
        r = requests.get(url)
        if r.status_code == 200:
            settings.sondaPresencia[objeto]['Status'] = r.text
        else:
            settings.sondaPresencia[objeto]['Status'] = "Desconocido"

def ordenarDhcpFijas(direccion):
    trozos = direccion["ip"].split('.')
    return (int(trozos[3]))
    
def getStaticDhcp():
    cnx = util.openDDBB()
        
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
    util.closeDDBB(cnx)
    return direcciones


@app.route("/presencia")
def presencia():
    getPresences()
    direcciones = dhcpLeases.getCurrentLeases()
    return render_template("redlocal.html", titulo = "Diseno Red", 
                            presencia = settings.sondaPresencia, tabla = direcciones) 
    
        
@app.route("/temperatura")
def temp():
    updateTemps()
    updateHumedad()
    return render_template("temperatura.html", titulo = "Temperatura", 
                            temperatura = settings.sondaTemp, humedad = settings.sondaHumedad) 

@app.route("/red")
def showRed():
    getPresences()
    
    direcciones = dhcpLeases.getCurrentLeases()

    ocupacion = dhcpLeases.agregarPorPool(direcciones)

    porcentajes = [None]*len(settings.poolMaxIPs)

    for i in range(len(settings.poolMaxIPs)):
        porcentajes[i] = ocupacion[i] / settings.poolMaxIPs[i] * 100

    return render_template("redlocal.html", titulo = "Diseño Red", 
                            presencia = settings.sondaPresencia, tabla = direcciones, 
                            agregados=ocupacion, poolMaxIPs=settings.poolMaxIPs, porcentajes=porcentajes)     


#    direcciones = dhcpLeases.getCurrentLeases()
#    direccionesFijas = getStaticDhcp()
    
    
#    return render_template("redlocal.html", titulo = "Diseno Red", 
#                            presencia = sondaPresencia, tabla = direcciones, tablaFija = direccionesFijas) 


@app.route("/raspberry")
def showRaspBerry():
    updateTemps()

    return render_template("raspberry.html", titulo = "Diseño RaspBerry PI",
                            temperatura = settings.sondaTemp) 

@app.route("/exterior")
def exterior():
    return render_template("exterior.html", titulo = "Exterior") 

@app.route("/")
def principal():
    return render_template("index.html", titulo = "Página Principal")

@app.route("/switch")
def swi():
    r = make_response(render_template('switch.html'))
    return r

@app.route("/historico")
def historico():
    vFechas, vValores = getHistorico()
    return render_template("historico.html", titulo = "Gráfico Histórico", fechas = vFechas, valores = vValores) 

    
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
