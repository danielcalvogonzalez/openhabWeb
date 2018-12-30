#! /usr/bin/python
# coding=utf-8

from mysql.connector import errorcode
import mysql.connector
import csv
import datetime
import sys

aExportar = {'Temperatura': {},
             'DespachoTemp': {},
             'BuhardillaTemp': {},
             'SotanoTemp': {},
             'RaspTemp1': {},
             'RaspTemp2': {}
            }

def write_data(query, filename, header):
    cursor.execute(query)

    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        writer.writerows(cursor)


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

query = "select * from Items"
cursor.execute(query)

for (Id, Name) in cursor:
    if Name in aExportar:
        aExportar[Name] = Id

for item in aExportar:
    query = "select * from Item{} where Time > current_date() - interval 1 week".format(aExportar[item])
    file = "static/csv/" + item + "-week.csv"
    write_data(query, file, ["Fecha", "Valor"])

    query = "select date_format(time, '%Y-%m-%d') as Fecha , round(avg(value),2) as Media, round(max(value),2) as Maximo, round(min(value),2) as Minimo from (select * from Item{} where Time > current_date() - interval 1 year) as sub group by date_format(time, '%Y-%m-%d')".format(aExportar[item])
    file = "static/csv/" + item + "-year.csv"
    write_data(query, file, ["Fecha", "Media", "Maximo", "Minimo"])

cursor.close()

cnx.close()

