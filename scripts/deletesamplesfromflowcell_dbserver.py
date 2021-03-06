#!/usr/bin/python
#Script that connects to the MySQL database and parses data from an html table
#Import the mysql.connector library/module
import sys
import MySQLdb as mysql
#from bs4 import BeautifulSoupi
import os.path
import time
import glob
import re

if len(sys.argv) == 2:
   fcname = sys.argv[1]
else:
  print ("\n\tUsage: "+sys.argv[0]+" flowcell\n")
  exit()

params = {}
with open("/home/hiseq.clinical/.scilifelabrc", "r") as confs:
  for line in confs:
    if len(line) > 5 and not line[0] == "#":
      line = line.rstrip()
      pv = line.split(" ")
      params[pv[0]] = pv[1]

now = time.strftime('%Y-%m-%d %H:%M:%S')
cnx = mysql.connect(user=params['CLINICALDBUSER'], port=int(params['CLINICALDBPORT']), host=params['CLINICALDBHOST'], passwd=params['CLINICALDBPASSWD'], db='clinstatsdb')
cursor = cnx.cursor()

print ("F: "+fcname)

cursor.execute(""" SELECT project.projectname, flowcell.flowcellname, sample.samplename, unaligned.lane, 
unaligned.readcounts, unaligned.yield_mb, TRUNCATE(q30_bases_pct,2), TRUNCATE(mean_quality_score,2),
flowcell.flowcell_id, sample.sample_id, unaligned.unaligned_id, unaligned.datasource_id, datasource.document_path,
supportparams.supportparams_id
FROM sample, flowcell, unaligned, project, datasource, supportparams
WHERE sample.sample_id     = unaligned.sample_id
AND   flowcell.flowcell_id = unaligned.flowcell_id
AND   sample.project_id    = project.project_id 
AND   datasource.datasource_id = unaligned.datasource_id
AND   datasource.supportparams_id = supportparams.supportparams_id
AND   flowcellname = '""" + fcname + """'
ORDER BY flowcellname, sample.samplename, lane """)
data = cursor.fetchall()
FCs = []
smpls = []
unals = []
srcs = []
srid = []
sprtps = []

if data:
  print "Project\tFlowcell\tSample\tLane\tRead counts\tyieldMB\t%Q30\tMeanQscore\tsource_id"
else:
  print "Flowcell " + fcname + " not found . . ."
for row in data:
  print row[0]+"\t"+row[1]+"\t"+str(row[2])+"\t"+str(row[3])+"\t"+str(row[4])+"\t"+str(row[5])+"\t"+str(row[6])+"\t"+str(row[7])+"\t"+str(row[11])
  try:
    exist = FCs.index(row[8])
  except ValueError:
    FCs.append(row[8])
  else:
    "Already added"
  try:
    exist = smpls.index(row[9])
  except ValueError:
    smpls.append(row[9])
  else:
    "Already added"
  try:
    exist = unals.index(row[10])
  except ValueError:
    unals.append(row[10])
  else:
    "Already added"
  try:
    exist = srcs.index(row[12])
  except ValueError:
    srcs.append(row[12])
  else:
    "Already added"
  try:
    exist = srid.index(row[11])
  except ValueError:
    srid.append(row[11])
  else:
    "Already added"
  try:
    exist = sprtps.index(row[13])
  except ValueError:
    sprtps.append(row[13])
  else:
    "Already added"


print "\n\tFound " + str(len(FCs)) + " flowcells, " + str(FCs).replace("L", "")
print "\tFound " + str(len(unals)) + " unaligned rows, " + str(unals).replace("L", "")
print "\tFound " + str(len(smpls)) + " samples, " + str(smpls).replace("L", "")
print "\tFound " + str(len(srcs)) + " sources, " + str(srcs).replace("L", "") + " ids " + str(srid).replace("L", "")
print "\tFound " + str(len(sprtps)) + " supportps, " + str(sprtps).replace("L", "")

yourreply = raw_input("\n\tDO YOU want to delete these statistics from the database? YES/[no] ")

if yourreply == "YES":
  print yourreply
else:
  print "\tnehe, will exit . .\n"
  cursor.close()
  cnx.close()
  exit(0)

print "Will delete unaligned"
for f in unals:
  try:
    cursor.execute(""" DELETE FROM unaligned WHERE unaligned_id = '{0}' """.format(f))
  except mysql.IntegrityError, e: 
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("DB error")
  except mysql.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("Syntax error")
  except mysql.Warning, e:
    print "Warning %d: %s" % (e.args[0],e.args[1])
    exit("MySQL warning")
  cnx.commit()
  print str(f) + " deleted "

print "Will delete sample"
for f in smpls:
  try:
    cursor.execute(""" DELETE FROM sample WHERE sample_id = '{0}' """.format(f))
  except mysql.IntegrityError, e:      
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("DB error")
  except mysql.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("Syntax error")
  except mysql.Warning, e:
    print "Warning %d: %s" % (e.args[0],e.args[1])
    exit("MySQL warning")
  cnx.commit()
  print str(f) + " deleted "

print "Will delete flowcell"
for f in FCs:
  try:
    cursor.execute(""" DELETE FROM flowcell WHERE flowcell_id = '{0}' """.format(f))
  except mysql.IntegrityError, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("DB error")
  except mysql.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("Syntax error")
  except mysql.Warning, e:
    print "Warning %d: %s" % (e.args[0],e.args[1])
    exit("MySQL warning")
  cnx.commit()
  print str(f) + " deleted "

print "Will delete datasource"
for f in srid:
  try:
    cursor.execute(""" DELETE FROM datasource WHERE datasource_id = '{0}' """.format(f))
  except mysql.IntegrityError, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("DB error")
  except mysql.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("Syntax error")
  except mysql.Warning, e:
    print "Warning %d: %s" % (e.args[0],e.args[1])
    exit("MySQL warning")
  cnx.commit()
  print str(f) + " deleted "

print "Will delete supportparams"
for f in sprtps:
  try:
    cursor.execute(""" DELETE FROM supportparams WHERE supportparams_id = '{0}' """.format(f))
  except mysql.IntegrityError, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("DB error")
  except mysql.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("Syntax error")
  except mysql.Warning, e:
    print "Warning %d: %s" % (e.args[0],e.args[1])
    exit("MySQL warning")
  cnx.commit()
  print str(f) + " deleted "

cnx.commit()
cursor.close()
cnx.close()
print "    done!"
