# coding=utf-8
#!/usr/bin/python3
# 
# Este codigo es usado desde el programa principal para
# mostrar el resultado de las leases activas de DHCP
#
from mysql.connector import errorcode
import mysql.connector
from isc_dhcp_leases import Lease, IscDhcpLeases
from util import printError

DHCP_LEASES_FILENAME = '/mnt/dhcp/dhcpd.leases'

# definir una clase
# los datos vendrán o de DHCP o del servidor SQL
#
# Añadir funcion print, comparar y ordenar
#


class IPObject(object):
    
    def __init__(self,ip):
        self.ip = ip
        self.name = ''
        self.mac = ''
        self.pool = -1
        self.poolName = ''
        
    def __repr__(self):
        return ("Object {} has {}, name {} in pool {} - {}".format(self.ip,self.mac,self.name,self.pool,self.poolName))
        
    
def ordenar(direccion):
    trozos = direccion.keys()[0].split('.')
    return (int(trozos[3]))

def ordenar1(direccion):
    trozos = direccion.ip.split('.')
    return (int(trozos[3]))

def getCurrentLeases1():
    leases = IscDhcpLeases(DHCP_LEASES_FILENAME)

    currentLeases = leases.get_current() 

    resultado = []

    for objeto in currentLeases.values():
        dispositivo      = IPObject(objeto.ip)
        dispositivo.name = objeto.hostname
        dispositivo.mac  = objeto.ethernet
        dispositivo.pool = 3
        dispositivo.poolName = 'DHCP'
        resultado.append(dispositivo)

# Ya tengo las direcciones de leases DHCP
#
# toca unir los resultados a las fijas y estáticas
 
    try:
        cnx = mysql.connector.connect(option_files="myopc.cnf")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            printError("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            printError("Database does not exist")
        else:
            printError(err)

    cursor = cnx.cursor()

    txtQuery = "select Descripcion from Dispositivos where Mac = %s"
    
    for objeto in resultado:
        print(objeto.mac)
        cursor.execute(txtQuery, (objeto.mac,))
        
        for nombre in cursor:
            print(nombre)
            objeto.name = nombre
        
    cursor.close()

    
    cursor = cnx.cursor()

    query = ("select Mac, IPAddress, Descripcion, Pool, PoolName from Dispositivos where Pool in (1,2,4)")
	
    cursor.execute(query)

    for mac, ip, desc, pool, poolName in cursor:
        dispositivo          = IPObject(ip.encode('ascii'))
        dispositivo.name     = desc
        dispositivo.mac      = mac.encode('ascii')
        dispositivo.pool     = pool
        dispositivo.poolName = poolName.encode('ascii')
        resultado.append(dispositivo)

    cursor.close()
    cnx.close()
    
    resultado.sort(key=ordenar1)
    
    return resultado

def getCurrentLeases():
    leases = IscDhcpLeases(DHCP_LEASES_FILENAME)

    currentLeases = leases.get_current() 

    resultado = []

    for objeto in currentLeases.values():
        item = {}
        item[objeto.ip] = objeto
        resultado.append(item)

    resultado.sort(key=ordenar)
    return resultado

"""
for objeto in resultado:
    direccion = objeto.values()[0]
    print objeto.keys()[0], direccion.ethernet, direccion.hostname, direccion.start, direccion.end
    print type(direccion.start)
    
"""
