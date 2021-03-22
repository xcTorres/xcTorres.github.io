https://ircama.github.io/osm-carto-tutorials/updating-data/

https://www.enterprisedb.com/postgres-tutorials/how-tune-postgresql-memory  


https://download.geofabrik.de/asia/malaysia-singapore-brunei.html  



https://stackoverflow.com/questions/3361291/slow-simple-update-query-on-postgresql-database-with-3-million-rows/24811058  


https://gis.stackexchange.com/questions/197393/use-local-osm-server-in-josm  


python36 + default
python36 + spark2.4
python36 + spark3.0  
custom_python + default 
custom_python + spark2.4
custom_python + spark3.0

 ---> Running in 287d1c857fe4
groupadd: group 'root' already exists
The command '/bin/sh -c true     && groupadd -g "${HADOOP_GID}" "${HADOOP_GROUP}"     && useradd -m -s /bin/bash -u "${HADOOP_UID}" -g "${HADOOP_GID}" -p "*" "${HADOOP_USER}"     && echo "${HADOOP_USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers     && true' returned a non-zero code: 9



with max_level_division as (
     select *, extend_fullname(array_append(parent_names, name::text)) as full_name
     from admin_division
     where level = 3 and geometry is not null 
 ), poi as (
     select nodes.id, hstore(array['admin_level_0','admin_level_1', 'admin_level_2', 'admin_level_3', 'admin_level_4'],
                                                     max_level_division.full_name) as admin_tag
     from nodes, max_level_division
     where nodes.tags != ''
     and  ST_intersects(max_level_division.geometry, nodes.geom) 
	 limit 100
 )

update nodes
set tags = tags || poi.admin_tag
from poi
where nodes.id = poi.id



Mar 16, 2021 4:20:40 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 1389644841, 324735.4529094181 objects/second.
Mar 16, 2021 4:20:45 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 2465698155, 471992.2015596881 objects/second.
Mar 16, 2021 4:20:50 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 3374102239, 491998.400319936 objects/second.
Mar 16, 2021 4:20:55 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 4474469047, 437154.3074155507 objects/second.
Mar 16, 2021 4:21:00 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 5039722520, 482066.9866026795 objects/second.
Mar 16, 2021 4:21:05 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 5252693122, 492546.09078184364 objects/second.
Mar 16, 2021 4:21:10 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 5541292165, 514586.16553378646 objects/second.
Mar 16, 2021 4:21:15 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 5787521333, 498805.83883223357 objects/second.
Mar 16, 2021 4:21:20 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 6130960962, 497395.5208958208 objects/second.
Mar 16, 2021 4:21:25 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 6657243594, 514063.5872825435 objects/second.
Mar 16, 2021 4:21:30 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Node 8260248054, 511628.34866053576 objects/second.
Mar 16, 2021 4:21:35 PM org.openstreetmap.osmosis.core.progress.v0_6.EntityProgressLogger process
INFO: Processing Way 27437504, 183526.45238570572 objects/second.  



Mar 17, 2021 6:54:41 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 6965864781 with action Modify, 87.74735158904657 objects/second.
Mar 17, 2021 6:54:46 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 6970756115 with action Modify, 93.03254142543422 objects/second.
Mar 17, 2021 6:54:51 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7001126098 with action Modify, 90.41916167664671 objects/second.
Mar 17, 2021 6:54:56 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7028918432 with action Modify, 95.58970265416085 objects/second.
Mar 17, 2021 6:55:01 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7032542749 with action Modify, 93.65015974440895 objects/second.
Mar 17, 2021 6:55:06 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7035062467 with action Modify, 90.20155657553383 objects/second.
Mar 17, 2021 6:55:11 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7043861975 with action Modify, 89.7640943622551 objects/second.
Mar 17, 2021 6:55:16 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7046397279 with action Modify, 88.02395209580838 objects/second.
Mar 17, 2021 6:55:21 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7046876255 with action Modify, 87.44260331403474 objects/second.
Mar 17, 2021 6:55:26 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7052467221 with action Modify, 86.84368137352764 objects/second.
Mar 17, 2021 6:55:31 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7060407996 with action Modify, 85.98280343931214 objects/second.
Mar 17, 2021 6:55:36 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7066524573 with action Modify, 92.4520766773163 objects/second.
Mar 17, 2021 6:55:41 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7086674163 with action Modify, 88.006385950908 objects/second.
Mar 17, 2021 6:55:46 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7098234820 with action Modify, 90.52757793764988 objects/second.
Mar 17, 2021 6:55:51 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7100522243 with action Modify, 77.24550898203593 objects/second.
Mar 17, 2021 6:55:56 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7104655704 with action Modify, 91.43541625074866 objects/second.
Mar 17, 2021 6:56:01 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7111917122 with action Modify, 95.40918163672654 objects/second.
Mar 17, 2021 6:56:06 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7112339611 with action Modify, 86.94783130121927 objects/second.
Mar 17, 2021 6:56:11 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7201973561 with action Modify, 87.1477113731761 objects/second.
Mar 17, 2021 6:56:16 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7206312080 with action Modify, 90.72741806554757 objects/second.
Mar 17, 2021 6:56:21 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7212416911 with action Modify, 90.74555266839896 objects/second.
Mar 17, 2021 6:56:26 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7236238839 with action Modify, 90.54567259644213 objects/second.
Mar 17, 2021 6:56:31 PM org.openstreetmap.osmosis.core.progress.v0_6.ChangeProgressLogger process
INFO: Processing Node 7385394978 with action Modify, 94.74315410753547 objects/second.
