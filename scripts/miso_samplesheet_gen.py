#!/usr/bin/python
### This script used to connect to mysql miso instance and get the Samplesheet
import pymysql
import fileinput
import csv
import os 
import sys

read1="adpread1"
read2="adpread2"

conn = pymysql.connect(host='miso.abudhabi.nyu.edu', port=13307, user='user', password='pass', database='lims', ssl_disabled='True')
cursor = conn.cursor()

#runid = int(input("Enter the runid to print: "))
runid = int(sys.argv[1])

query = 'SELECT distinct  l.name, l.alias , ind1.name,ind1.sequence, ind2.name, ind2.sequence FROM Run r  JOIN Run_SequencerPartitionContainer rspc ON rspc.Run_runId = %s  JOIN SequencerPartitionContainer spc ON spc.containerId = rspc.containers_containerId  JOIN _Partition part ON part.containerId = spc.containerId  JOIN Pool pool ON pool.poolId = part.pool_poolId  JOIN Pool_LibraryAliquot pla ON pla.poolId = pool.poolId  JOIN LibraryAliquot la ON la.aliquotId = pla.aliquotId  JOIN Library l ON l.libraryId = la.libraryId  JOIN Sample s ON s.sampleId = l.sample_sampleId  Join Indices ind1 ON  ind1.indexId =l.index1Id LEFT Join Indices ind2 ON  ind2.indexId =l.index2Id;'


cursor.execute(query, (runid,))
#cursor.execute(query)
with open("output1.csv","w") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(col[0] for col in cursor.description)
    for row in cursor:
        writer.writerow(row)

## This uses pandas to extract the csv
#results = pandas.read_sql_query(query, conn)
#results.to_csv("output.csv", index=False)


inputFileName = "output1.csv"
outputFileName = os.path.splitext(inputFileName)[0] + "_modified.csv"
out = "SampleSheet.csv"

with open(inputFileName, 'r') as inFile, open(outputFileName, 'w') as outfile:
    r = csv.reader(inFile)
    w = csv.writer(outfile)

    next(r, None)  # skip the first row from the reader, the old header
    # write new header
    w.writerow(["[Settings]"])
    w.writerow(["Adapter", "r1"])  
    w.writerow(["AdapterRead2", "r2"])
    w.writerow([])
    w.writerow(["[Data]"])
    w.writerow(['Sample_ID', 'Sample_Name', 'I7_Index_ID', 'index', 'I5_Index_ID', 'index2'])  

    # copy the rest
    for row in r:
        w.writerow(row)

with fileinput.FileInput(outputFileName, inplace=True) as file:
    for line in file:
        print(line.replace("r1", read1), end='')

with fileinput.FileInput(outputFileName, inplace=True) as file:
    for line in file:
        print(line.replace("r2", read2), end='')

os.rename(outputFileName, out)
os.remove("output1.csv")

