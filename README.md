# Dota2_Player_Classification

## Directory structure
1. root directory contains all the clustering and classification models
  1. gen_dataset.ipynb contains all the functions that using Dota2 API to retrieve raw data, and build the clustering models
  2. Dota2_classification.ipynb builds all the classification models
  3. 1_xxx_yyy_zzz.csv - 10_xxx_yyy_zzz.csv is the output of clustring of a attribute sets, it is also the input of classification models
  4. 1_players_model.csv - 10_players_model.csv is the raw data(filtered) we get from the Dota2 API
 
2. Web directory contains the web application 
  1. Server.py is the backend 
    1. 10 models will be loaded during the initialization
  2. models contains the 10 models
  3. ojb contains the cached queries
  4. templates/index is the frontend 
    1. The Javascript function Update() is the enterance of the D3 code

## How to run the demo

### dependency
1. Flask
2. urllib2
3. numpy
4. pandas
5. pyspark

### instruction
1. export FLASK_APP = "server.py"
2. flask run
3. access to 127.0.0.0:5000
  

## Dota2 API: 
https://dota2api.readthedocs.io/en/latest/
https://docs.opendota.com/

