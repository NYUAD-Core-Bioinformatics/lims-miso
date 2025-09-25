#!/usr/bin/python
### This script used to connect to mysql miso instance and get the Samplesheet on 10X genomics
import pymysql
import fileinput
import csv
import os 
import sys
import subprocess

conn = pymysql.connect(host='miso.abudhabi.nyu.edu', port=3307, user='user', password='pass', database='lims', ssl_disabled='True')
cursor = conn.cursor()

#runid = int(input("Enter the runid to print: "))
runid = int(sys.argv[1])

query = 'SELECT distinct  l.alias , ind1.name FROM Run r  JOIN Run_SequencerPartitionContainer rspc ON rspc.Run_runId = %s  JOIN SequencerPartitionContainer spc ON spc.containerId = rspc.containers_containerId  JOIN _Partition part ON part.containerId = spc.containerId  JOIN Pool pool ON pool.poolId = part.pool_poolId  JOIN Pool_LibraryAliquot pla ON pla.poolId = pool.poolId  JOIN LibraryAliquot la ON la.aliquotId = pla.aliquotId  JOIN Library l ON l.libraryId = la.libraryId  JOIN Sample s ON s.sampleId = l.sample_sampleId  Join Indices ind1 ON  ind1.indexId =l.index1Id LEFT Join Indices ind2 ON  ind2.indexId =l.index2Id;'


cursor.execute(query, (runid,))
with open("output1.csv","w") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(col[0] for col in cursor.description)
    for row in cursor:
        writer.writerow(row)

inputFileName = "output1.csv"
outputFileName = os.path.splitext(inputFileName)[0] + "_modified.csv"
out = "10xsimple.csv"

with open(inputFileName, 'r') as inFile, open(outputFileName, 'w') as outfile:
    r = csv.reader(inFile)
    w = csv.writer(outfile)

    next(r, None)  # skip the first row from the reader, the old header
    w.writerow(['Lane', 'Sample', 'Index'])  

    # copy the rest
    for row in r:
        w.writerow(row)

#To add * sign to the beginining of each line
for line in fileinput.input([outputFileName], inplace=True):
    sys.stdout.write('*,{l}'.format(l=line))


#To remove "*," from the first line
with open(outputFileName, 'r') as fin:
    header = fin.read(2)
    lines = fin.readlines()
with open(outputFileName, 'w') as fout:
    fout.writelines(lines)

os.rename(outputFileName, out)
#Removes 0's in the index value
#for eg:- it changes from SI-GA-E06 NOT SI-GA-E6
subprocess.call(["sed -i 's/0*\([0-9]*$\)/\\1/'  10xsimple.csv"], shell=True)

#Removes "." and "whitespaces" in Samplename field
subprocess.call(["awk -i inplace 'BEGIN{FS=OFS=\",\"}/^\*+,/{gsub(/[\.\" \"<`\\x27]/,\"_\",$2);print;next}1' 10xsimple.csv"], shell=True)

os.remove("output1.csv")

