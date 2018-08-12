from flask import Flask, render_template
import mysql.connector

from mysql.connector import errorcode

Despacho = -1
Buhardilla = -1
Sotano = -1
Exterior = -1
Temperaturas = {}

app = Flask(__name__)

def getTemp(Sensor):
    try:
        cnx = mysql.connector.connect(user="openhabSQL", password="", host="192.168.24.5", database = "openhab2")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
         print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cursor = cnx.cursor()

    query = ("select * from {} order by Time desc limit 1".format("Item" + str(Sensor)))

    cursor.execute(query)

    when = now = 0
    for (momento, valor ) in cursor:
#        print("** {} {} ".format(momento, valor))
#        print("Tipo {} y {}".format(type(momento), type(valor)))
        when = momento
        now = valor

    cursor.close()
    cnx.close()
    return valor


@app.route("/temperatura")
def temp():
    updateTemps()
    return render_template("temperatura.html", titulo = "Temperatura-1", 
                            temperatura = Temperaturas) 


@app.route("/red")
def showRed():
    return render_template("redlocal.html", titulo = "Diseno Red") 

def updateTemps():
    Temperaturas['despacho'] = getTemp(Despacho) if Despacho != -1 else -99
    Temperaturas['sotano'] = getTemp(Sotano) if Sotano != -1 else -99
    Temperaturas['buhardilla'] = getTemp(Buhardilla) if Buhardilla != -1 else -99
    Temperaturas['exterior'] = getTemp(Exterior) if Exterior != -1 else -99

#
# Comienzo
#

try:
    cnx = mysql.connector.connect(user="openhabSQL", password="", host="192.168.24.5", database = "openhab2")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
       print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

cursor = cnx.cursor()

query = ("SELECT * from Items")

cursor.execute(query)

for (itemId, itemName ) in cursor:
    if itemName == "DespachoTemp":
        Despacho = itemId
    if itemName == "SotanoTemp":
        Sotano = itemId
    if itemName == "BuhardillaTemp":
        Buhardilla = itemId
    if itemName == "Temperatura":
        Exterior = itemId

cursor.close()

if Despacho != -1:
    Temperaturas['despacho'] = getTemp(Despacho)
if Sotano != -1:
    Temperaturas['sotano'] = getTemp(Sotano)
if Buhardilla != -1:
    Temperaturas['buhardilla'] = getTemp(Buhardilla)
if Exterior != -1:
    Temperaturas['exterior'] = getTemp(Exterior)

"""
print("Despacho {}".format(Despacho))
print("Sotano   {}".format(Sotano))
print("Buhardil {}".format(Buhardilla))

print("Tipo {}", type(Despacho))
"""

print(Temperaturas)


if __name__ == "__main__":
    app.run(host='0.0.0.0')

cnx.close()
