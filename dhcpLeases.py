# coding=utf-8
#!/usr/bin/python3
# 
# Este codigo es usado desde el programa principal para
# mostrar el resultado de las leases activas de DHCP
#
from mysql.connector import errorcode
import mysql.connector
from isc_dhcp_leases import Lease, IscDhcpLeases

import util

DHCP_LEASES_FILENAME = '/mnt/dhcp/dhcpd.leases'

# definir una clase
# los datos vendrán o de DHCP o del servidor SQL
#
# Añadir funcion print, comparar y ordenar
#


class IPObject(object):
    
    def __init__(self,ip):
        self.ip    = ip
        self.name  = ''
        self.mac   = ''
        self.pool  = -1
        self.poolName = ''
#@ self.endDate        
        
        
    def __repr__(self):
        return ("Object {} has {}, name {} in pool {} - {}".format(self.ip,self.mac,self.name,self.pool,self.poolName))
        
def contarPorPool(lista, tipoPool):
    nCuantos = 0
    for objeto in lista:
        if objeto.pool == tipoPool:
            nCuantos+=1
    return nCuantos

def agregarPorPool(lista):
    contadores = {}
    maximo=-1
    for objeto in lista:
        if objeto.pool in contadores:
            contadores[objeto.pool] += 1
        else:
            contadores[objeto.pool] = 1
        if objeto.pool > maximo:
            maximo = objeto.pool
    lista=[None]*maximo
    for key, value in contadores.items():
        lista[key-1] = value
    return lista

def oldOrdenar(direccion):
    trozos = direccion.keys()[0].split('.')
    return (int(trozos[3]))

def ordenar(direccion):
    trozos = direccion.ip.split('.')
    return (int(trozos[3]))

def getCurrentLeases():
    leases = IscDhcpLeases(DHCP_LEASES_FILENAME)

    currentLeases = leases.get_current() 

    resultado = []

    for objeto in currentLeases.values():
        dispositivo      = IPObject(objeto.ip)
        dispositivo.name = objeto.hostname
        dispositivo.mac  = objeto.ethernet.upper()
        dispositivo.pool = 3
        dispositivo.poolName = 'DHCP'
        dispositivo.endDate  = objeto.end
        resultado.append(dispositivo)

# Ya tengo las direcciones de leases DHCP
#
# toca unir los resultados a las fijas y estáticas
 
    cnx = util.openDDBB()

    cursor = cnx.cursor()

    txtQuery = "select Descripcion from Dispositivos where Mac = %s"
    
    for objeto in resultado:
        
        cursor.execute(txtQuery, (objeto.mac,))
        
        for nombre in cursor:
            objeto.name = nombre[0]
        
    cursor.close()

    
    cursor = cnx.cursor()

    query = ("select Mac, IPAddress, Descripcion, Pool, PoolName from Dispositivos where Pool in (1,2,4)")
	
    cursor.execute(query)

    for mac, ip, desc, pool, poolName in cursor:
        dispositivo          = IPObject(ip)
        dispositivo.name     = desc
        dispositivo.mac      = mac.upper()
        dispositivo.pool     = int(pool)
        dispositivo.poolName = poolName
        dispositivo.endDate  = 'N/A'
        resultado.append(dispositivo)

    cursor.close()

    util.closeDDBB(cnx)
    
    resultado.sort(key=ordenar)
    
    return resultado

def _oldGetCurrentLeases():
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
