#!/usr/bin/python
#Script that connects to the MySQL database and parses data from an html table
#Import the mysql.connector library/module
#
#  from the bash script starting qc parsing to db
#  /home/clinical/SCRIPTS/parseunaligned_dbserver.py /home/clinical/DEMUX/${RUN}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv
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


query1 = """ SELECT projectname, samplename, GROUP_CONCAT(sample.sample_id), MIN(sample.sample_id), 
             unaligned_id, COUNT(sample.sample_id)
             FROM sample,project,unaligned 
             WHERE project.project_id = sample.project_id AND unaligned.sample_id = sample.sample_id GROUP BY samplename """
cursor.execute(query1)
for row in cursor.fetchall():
  if row[5] > 1:
    ids = row[2].split(',')
    for id in ids:
      query2 = " UPDATE TABLE unaligned SET sample_id = '"+str(row[3])+"' WHERE sample_id IN ("+row[2]+") " 
      print query2

exit(0)