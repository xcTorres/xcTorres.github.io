https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables  



curl --location --request POST 'http://poi-compare.ds.uat.shopee.io/geocoding_batch' \
--header 'Content-Type: application/json' \
--data-raw '{
    "requests": [
        {
        "address": "23 Bến Thủy",
        "address_level1": "NGHỆ AN",
        "address_level2":"THÀNH PHỐ VINH",
        "experiment": 0
        }
    ],
    "components": "country:VN",

    "key": "l2pUf24TuesNkHG9hTWP7sU1EsVEhan9eC94cDL7",
    "request_id": "",
    "use_case": "<USER-IDENTIFICATION>"
}'
                                                                                          

                                                                               curl --location --request POST 'http://localhost:8021/geocoding_batch' \              
--header 'Content-Type: application/json' \
--data-raw '{
    "requests": [{"address": "No.9793, Jalan Teratai 10, Taman Maju, 77000", "address_level1": "Melaka", "address_level2": "Jasin", "address_level3": "", "zipcode": "77000", "place_id": "dspoi_202106_271643_2138893834078_p202106_1"}],
    "components": "country:MY",

    "key": "l2pUf24TuesNkHG9hTWP7sU1EsVEhan9eC94cDL7",
    "request_id": "",
    "use_case": "<USER-IDENTIFICATION>"
}'
