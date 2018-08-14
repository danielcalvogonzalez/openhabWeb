import mysql.connector

from mysql.connector import errorcode

Despacho = -1
Buhardilla = -1
Sotano = -1
Temperaturas = {}

def getTemp(Sensor):
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
    return valor


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

cursor.close()

if Despacho != -1:
    Temperaturas['Despacho'] = getTemp(Despacho)
if Sotano != -1:
    Temperaturas['Sotano'] = getTemp(Sotano)
if Buhardilla != -1:
    Temperaturas['Buhardilla'] = getTemp(Buhardilla)

"""
print("Despacho {}".format(Despacho))
print("Sotano   {}".format(Sotano))
print("Buhardil {}".format(Buhardilla))

print("Tipo {}", type(Despacho))
"""

print(Temperaturas)


cnx.close()