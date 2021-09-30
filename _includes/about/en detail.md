# Chong Xie (谢冲)

### Contact Infomation

- Email：xcwhu2016@gmail.com 
- Wechat：xc_19931112
- Instagram：xctorres8


### Education

| Master’s degree, Geographic Information Science and Cartography<br>Wuhan University, China| Sep 2016 – Jun 2019 |
| Bachelor’s degree, Photogrammetry and Remote Sensing <br>Wuhan University, China | Sep 2012 – Jun 2016 |


### Course  

| Course | Certificate| Time |  
| [Udemy  Graph Theory Algorithms](https://www.udemy.com/course/graph-theory-algorithms/) |[https://www.udemy.com/certificate/UC-0791cf8e-2e82-41a5-8224-bd96b3ba8530/](https://www.udemy.com/certificate/UC-0791cf8e-2e82-41a5-8224-bd96b3ba8530/)| Dec 2020 |


### Work Experience
**Jan 2021 - Present , Singapore**  
**Senior Data Scientist**  

- **EAT improvement**  
The project is to improve the accuracy of ETA using drivers' trajectories. First We collect the GPS records using Kafka, which includes the GPS location, speed, direction and etc. And It groups the GPS records into trajectory segments by driver ID and time buckets. We snap the raw trajectory segments onto the road links. And then we update the speed for the road links whose count are greater than certain threshold. For the road links whose count are less than the threshold, we update the speed by regions and road types. As a result,
<br>

- **Device positioning service**  
The project is to predict the user location given WIFI macAddress using Bayesian model. In the training data, it calculates geoohashes of each WIFI, and group the counts by signal bins under each geohash grid. All of WIFI and according geohash counts are stored in Redis cluster. In order to reduce the memory, we redesign the schema and compress the data, as a result, it saves half memory. In the prediction part, we use Bayesian model，and add higher priority to the probability of geohash grid. As a result, the median of distance difference is 43 meter, and the 90 percentile is 598 meter.
<br>

- **Map database**  
MapDB is a database to manage map data, including point(POI), linestring(roads), and polygons(admin division and AOI). Using PostGIS, the database supports spatial query, and join the admin table and other tables in order to add admin division attribute to them.
<br>

**Jul 2019 - Jan 2021 , Singapore**  
**Shopee Data Scientist**
- **Batch assignment project**  
The batch assignment is used to assign the orders to shippers in global optimization(one shipper is allowed to accept one order only). We use hungarian algorithms and machine learning model(lightGBM) to optimize the assignment. As a result, the mean of single assign successfully rate is increased from 95.29% to 97.15%, the average of assign ignore rate has been reduced from 24.36% to 10%, the average of time from auto-assign to last in-charge has been reduced from 17.05s to 13.75s.  
<br>

- **Route engine service**    
In logistics and assignment business, it is of great importance to have a API service of getting the routing distance between coordinates. Before our own route engine service is born, Shopee uses google map service, but it costs hundreds of thousands of dollars per month. Based on open-source data, we provide our own direction and matrix API using Contraction Hierarchies algorithm.   


**Sep 2018 – Jun 2019 , Wuhan, China**  
**Huawei Wuhan   Intern**
- Participate in developing a spatio-temporal database system based on HBase, which is an innovative project of Huawei in the field of IoT.
- Design the spatio-temporal index and improve the performance of range query and k-NN query, making the average query time under 100 ms.  

**Jun 2018 – Sep 2018 , Beijing, China**  
**DiDi   Intern**
- Participate in utilizing the machine learning model to provide the appropriate drop-off point for the destination, saving passenger’s time and walking cost.
- Combine the features of POI, passengers, drivers, road, etc. ,and utilize GBDT model to screen out important features, resulting in 10% decrease the MAE of destination deviation.

---

### Skill  
**Programming Language:** Python, Java, C++  
**Other Skills:** Spark, Redis, Airflow

### Publication  

[MAP-Vis: A Distributed Spatio-Temporal Big Data Visualization Framework Based on a MultiDimensional Aggregation Pyramid Model](https://www.mdpi.com/2076-3417/10/2/598/htm)

