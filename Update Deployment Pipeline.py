# Databricks notebook source
model_serving_endpoint_name ='ProxyModel'
proxy_model_name = 'ProxyModel'
proxy_model_version = 3

instance = "XYZ.cloud.databricks.com"
token = "XYZ"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
  }

# COMMAND ----------

import requests
import json
endpoint_url = f"https://{instance}/api/2.0/serving-endpoints"
url = f"{endpoint_url}/{model_serving_endpoint_name}"
json_obj = json.loads(requests.get(url, headers=headers).text)
s = json_obj['config']['served_models'][0]['name']

# COMMAND ----------

served_model_name = s
my_json = {
  "name": model_serving_endpoint_name,
  "config": {
   "served_models": [{
     "name": served_model_name,
     "model_name": proxy_model_name,
     "model_version": proxy_model_version,
     'workload_type': 'CPU',
     "workload_size": "Small",
     "scale_to_zero_enabled": True,
     'environment_vars': {
      'MLFLOW_REGISTRY_URI': '{{secrets/bilal-model-registry/target-host}}',
      'MLFLOW_TRACKING_TOKEN': '{{secrets/bilal-model-registry/target-token}}'
      },
   }],
    "traffic_config":{
    "routes":[
      {
          "served_model_name": served_model_name,
          "traffic_percentage":"0"
      },
    ]
  }
 }
}

# COMMAND ----------

# the below section of code updates the json to add a new served model name

#create a name for new served model
parts = s.split("-")
if len(parts) > 1:
    parts[1] = str(int(parts[1]) + 1)
else:
    parts.append('1')
new_s = "-".join(parts)

# copy and add a new served model name
new_model = my_json["config"]['served_models'][0].copy()
new_model['name'] = new_s
my_json["config"]['served_models'].append(new_model)
new_route = {'served_model_name': new_s, 'traffic_percentage': 100}
my_json["config"]['traffic_config']['routes'][0]['traffic_percentage'] = 0
my_json["config"]['traffic_config']['routes'].append(new_route)

# COMMAND ----------

def func_create_endpoint(model_serving_endpoint_name):
  headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
  }
  #get endpoint status
  endpoint_url = f"https://{instance}/api/2.0/serving-endpoints"
  url = f"{endpoint_url}/{model_serving_endpoint_name}"
  r = requests.get(url, headers=headers)
  if "RESOURCE_DOES_NOT_EXIST" in r.text:  
    print("Creating this new endpoint: ", f"https://{instance}/serving-endpoints/{model_serving_endpoint_name}/invocations")
    re = requests.post(endpoint_url, headers=headers, json=my_json)
  else:
    new_model_version = (my_json['config'])['served_models'][0]['model_version']
    print("This endpoint existed previously! We are updating it to a new config with new model version: ", new_model_version)
    # update config
    url = f"{endpoint_url}/{model_serving_endpoint_name}/config"
    re = requests.put(url, headers=headers, json=my_json['config']) 
    # wait till new config file in place
    import time,json
    #get endpoint status
    url = f"https://{instance}/api/2.0/serving-endpoints/{model_serving_endpoint_name}"
    retry = True
    total_wait = 0
    while retry:
      r = requests.get(url, headers=headers)
      assert r.status_code == 200, f"Expected an HTTP 200 response when accessing endpoint info, received {r.status_code}"
      endpoint = json.loads(r.text)
      if "pending_config" in endpoint.keys():
        seconds = 10
        print("New config still pending")
        if total_wait < 6000:
          #if less the 10 mins waiting, keep waiting
          print(f"Wait for {seconds} seconds")
          print(f"Total waiting time so far: {total_wait} seconds")
          time.sleep(10)
          total_wait += seconds
        else:
          print(f"Stopping,  waited for {total_wait} seconds")
          retry = False  
      else:
        print("New config in place now!")
        retry = False
  assert re.status_code == 200, f"Expected an HTTP 200 response, received {re.status_code}"

# COMMAND ----------

func_create_endpoint(model_serving_endpoint_name)

# COMMAND ----------

served_model_name = new_s
my_json = {
  "name": model_serving_endpoint_name,
  "config": {
   "served_models": [{
     "name": served_model_name,
     "model_name": proxy_model_name,
     "model_version": proxy_model_version,
     'workload_type': 'CPU',
     "workload_size": "Small",
     "scale_to_zero_enabled": True,
     'environment_vars': {
      'MLFLOW_REGISTRY_URI': '{{secrets/bilal-model-registry/target-host}}',
      'MLFLOW_TRACKING_TOKEN': '{{secrets/bilal-model-registry/target-token}}'
      },
   }],
    "traffic_config":{
    "routes":[
      {
          "served_model_name": served_model_name,
          "traffic_percentage": "100"
      },
    ]
  }
 }
}

# COMMAND ----------

func_create_endpoint(model_serving_endpoint_name)

# COMMAND ----------


