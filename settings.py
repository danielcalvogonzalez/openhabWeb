#!/usr/bin/python3
# coding=utf-8

opt_debug = False

UPDATE_INTERVAL = 20		# Tiempo máximo que si no ha habido actualización, se declara como offline

SERVER_ADDRESS_LABEL = 'http://192.168.24.6:8080/rest/items/{0}'
SERVER_ADDRESS_STATE = 'http://192.168.24.6:8080/rest/items/{0}/state'

sondaTemp      = {}
sondaHumedad   = {}
sondaPresencia = {}

poolMaxIPs = [15, 34, 101, 7]