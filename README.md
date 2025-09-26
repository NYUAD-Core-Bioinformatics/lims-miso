# lims-miso

This document explains the installation and upgrade of Miso Lims application based on docker compose. 

The best way to install miso lims is with the docker based. 

### Prerequisites

Docker CE >= 26.1
Miso v3.11.0

#### Directory structure as follows:- 

You need to maintain the data directory for lims as follows.

```
/data/miso/miso-data-directory/
├── conf
├── creds_db
├── files
├── logs
├── mysql
└── nginx
```

Place ```miso.properties``` file the conf directory. 
Place ```ssl.conf``` in nginx folder.

#### Install Instructions

Define the enviroment variable as below. 

```
cat /data/miso/miso-installer/.env
MISO_DB_USER=tgaclims
MISO_DB=lims
MISO_DB_PASSWORD_FILE=./.miso_db_password
MISO_ROOT_PASSWORD_FILE=./.miso_root_password
MISO_TAG=3.11.0
```

##### Clone the repo 

```
git clone https://github.com/NYUAD-Core-Bioinformatics/lims-miso
cd lims-miso
docker compose up -d 
```

On a new terminal, this is to increase the length of sequnece column 

```
$docker exec -it miso-installer-db-1  /usr/bin/mysql -u root --password=<pass>
use LIMS;
ALTER TABLE Indices MODIFY COLUMN sequence VARCHAR(100);
```


Enable addition character for the adapter sequence string. This can be modify from ```${tomcat-home}/webapps/ROOT/scripts/header_script.js`

On v3.11.0 - header_script.js,
```
 307 data:"family.name",type:"text",disabled:!0},{title:"Position",data:"position",type:"dropdown",source:[1,2],required:!0},{title:"Name",data:"name",type:"text",maxLength:50,required:!0},{title:"Demultiplexing Name",data:"sequence",type:"text"     ,maxLength:24,required:!0,include:!!b.indexFamily.fakeSequence},{title:"Sequence",data:"sequence",type:"text",maxLength:120,required:!0,regex:"^[ACGTKYR+]+$",description:"Can only include the characters [A, C, G, T, K, Y, R, +]",include:!b.     indexFamily.fakeSequence},{title:"Sequences",
```

Simply apply this change by 
```
docker cp header_script.js miso-installer-webapp-1:/usr/local/tomcat/webapps/ROOT/scripts/header_script.js
docker compose restart
```

Miso LIMS  treats jira domain SSL certs as self signed cert due to unknown reason. In this case, community suggested to apply the cert to the keystore manually.
https://github.com/miso-lims/miso-lims/issues/2640

To obtain the cert from cbi.abudhabi.nyu.edu

```
echo | openssl s_client -servername google.com -connect cbi.abudhabi.nyu.edu:443 |sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p'  > certificate.crt
```

Supply ```changeit``` as the pass for the keystore pass.
```
docker cp certificate.crt miso-installer-webapp-1:/tmp/
docker exec -it miso-installer-webapp-1 bash
keytool -importcert -trustcacerts -cacerts -alias jira_miso_lims -file /tmp/certificate.crt
```

Access the service via ```https://miso.abudhabi.nyu.edu```

Note:- Below task only  for Miso upgrade. 

If you already have a miso MYSQL v8 database dump, and if you would like to take database dump and import. Use below 

```
To  dump 

/usr/bin/docker exec miso-installer-db-1 /bin/bash -c "/usr/bin/mysql -u tgaclims -p<pass> --skip-column-names -b -e 'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = \"lims\" AND TABLE_TYPE = \"BASE TABLE\";' 2> /dev/null | /usr/bin/xargs /usr/bin/mysqldump -u tgaclims -p<pass> --single-transaction --skip-triggers lims 2> /dev/null" > /data/miso_backup/db_back/db_cron_job_back/lims_$(date "+%y-%m-%d-%H-%M-%S").sql 2>&1

```

Then on another terminal
```
$docker exec -it miso-installer-db-1  /usr/bin/mysql -u root --password=<pass>
>DROP DATABASE lims;
>CREATE DATABASE lims;
>GRANT ALL ON `lims`.* TO 'tgaclims'@'%';

Then restore the dump
docker exec -i miso-installer-db-1 sh -c "exec mysql -u root -p<pass> lims" < lims_25-09-24-05-00-01.sql
```


Samplesheet Generation script can be found in ```scripts``` folder.

#### Other Useful Links

- [MISO LIMS](https://github.com/miso-lims/miso-lims)
- [Docker](https://www.docker.com/)
- [Lims Introductory Video](https://youtu.be/vE5mFv-zMpk)