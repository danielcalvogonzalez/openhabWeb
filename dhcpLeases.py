# coding=utf-8

from isc_dhcp_leases import Lease, IscDhcpLeases

def ordenar(direccion):
    trozos = direccion.keys()[0].split('.')
    return (int(trozos[3]))

def getCurrentLeases():
    leases = IscDhcpLeases('/mnt/dhcp/dhcpd.leases')

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