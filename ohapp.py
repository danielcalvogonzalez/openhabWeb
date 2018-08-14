# coding=utf-8

from flask import Flask, render_template
from mysql.connector import errorcode
import mysql.connector
import datetime

sondaTemp = {'Temperatura': {},
             'DespachoTemp': {},
             'BuhardillaTemp': {},
             'SotanoTemp': {},
             'RaspTemp1': {},
             'RaspTemp2': {}
            }

app = Flask(__name__)

def getTemp(Sensor):
    try:
        cnx = mysql.connector.connect(option_files="myopc.cnf")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
         print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

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
        cnx = mysql.connector.connect(option_files="myopc.cnf")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
         print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

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
    for objeto in sondaTemp:
        sondaTemp[objeto]['Data'] = getTempEx(sondaTemp[objeto])

@app.route("/temperatura")
def temp():
    updateTemps()
    return render_template("temperatura.html", titulo = "Temperatura-1", 
                            temperatura = sondaTemp) 

@app.route("/red")
def showRed():
    return render_template("redlocal.html", titulo = "Diseño Red") 

@app.route("/raspberry")
def showRaspBerry():
    updateTemps()

    return render_template("raspberry.html", titulo = "Diseno RaspBerry PI",
                            temperatura = sondaTemp) 

@app.route("/")
def principal():
    return render_template("index.html")

#
# Comienzo
#

try:
    cnx = mysql.connector.connect(option_files="myopc.cnf")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
       print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

cursor = cnx.cursor()

query = ("SELECT * from Items where ItemName = %s")

for objeto in sondaTemp:
    cursor.execute(query, (objeto, ))

    for (itemId, itemName ) in cursor:
        sondaTemp[objeto]['ID'] = 'Item' + str(itemId)

cursor.close()

cnx.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0')

