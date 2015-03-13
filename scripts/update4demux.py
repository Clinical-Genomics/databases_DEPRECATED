#!/usr/bin/python
#Script that connects to the MySQL database and parses data from an html table
#Import the mysql.connector library/module
#
#
import sys
import MySQLdb as mysql
import time
import glob
import re
import socket
import os

message = ("usage: "+sys.argv[0]+" <config_file:optional>")
print message


configfile = "/home/hiseq.clinical/.scilifelabrc"
if (len(sys.argv)>1):
  if os.path.isfile(sys.argv[1]):
    configfile = sys.argv[1]
    print "Using config "+configfile
else:
  print "No config file given."

params = {}
with open(configfile, "r") as confs:
  for line in confs:
    if len(line) > 5 and not line[0] == "#":
      line = line.rstrip()
      pv = line.split(" ")
      params[pv[0]] = pv[1]
      
now = time.strftime('%Y-%m-%d %H:%M:%S')
# this script is written for database version:
_VERSION_ = params['DBVERSION']

cnx = mysql.connect(user=params['CLINICALDBUSER'], port=int(params['CLINICALDBPORT']), host=params['CLINICALDBHOST'], 
                    passwd=params['CLINICALDBPASSWD'], db=params['STATSDB'])
cursor = cnx.cursor()

cursor.execute(""" SELECT major, minor, patch FROM version ORDER BY time DESC LIMIT 1 """)
row = cursor.fetchone()
if row is not None:
  major = row[0]
  minor = row[1]
  patch = row[2]
else:
  sys.exit("Incorrect DB, version not found.")
if (str(major)+"."+str(minor)+"."+str(patch) == _VERSION_):
  print "Correct database version "+str(_VERSION_)+"   DB "+params['STATSDB']
else:
  exit ("Incorrect DB version. This script is made for "+str(_VERSION_)+" not for "
         +str(major)+"."+str(minor)+"."+str(patch))

print "Database: "+params['STATSDB']
yourreply = raw_input("\n\tDO YOU want to restructure this database? YES/[no] ")
if yourreply != "YES":
  exit()

query1 = """ SELECT datasource_id, samplename, GROUP_CONCAT(DISTINCT sample.sample_id), MIN(sample.sample_id), 
             unaligned_id, COUNT(DISTINCT sample.sample_id)
             FROM sample,project,unaligned 
             WHERE project.project_id = sample.project_id AND unaligned.sample_id = sample.sample_id GROUP BY samplename """
             
query2 = """ SELECT datasource.datasource_id, unaligned_id, flowcellname, commandline
             FROM flowcell, datasource, unaligned, supportparams 
             WHERE unaligned.flowcell_id = flowcell.flowcell_id 
             AND supportparams.supportparams_id = datasource.supportparams_id
             AND flowcell.datasource_id = datasource.datasource_id """
cursor.execute(query2)
for row in cursor.fetchall():
  clas = row[3].split('\n')
  isbm = False:
  for cla in clas:
    if isbm:
      basemask = cla
      isbm = False
    if cla == "  '--use-bases-mask',":
      isbm = True
  print row[0], row[1], row[2], basemask
#  if row[5] > 1:
#    ids = row[2].split(',')
#    for id in ids:
#      query2 = " UPDATE unaligned SET sample_id = '"+str(row[3])+"' WHERE sample_id IN ("+row[2]+") " 
#      try:
#        cursor.execute(query2)
#      except mysql.IntegrityError, e:
#        print "Error %d: %s" % (e.args[0],e.args[1])
#        exit("DB error")
#      except mysql.Error, e:
#        print "Error %d: %s" % (e.args[0],e.args[1])
#        exit("Syntax error")
#      except mysql.Warning, e:
#        print "Warning %d: %s" % (e.args[0],e.args[1])
#        exit("MySQL warning")
#      cnx.commit()
#      print "done "+query2

exit(0)
