# Databricks notebook source
proxy_model_name = "ProxyModel"
target_model = "passthrough"
model_serving_endpoint_name = "ProxyModel"

instance = "XYZ.cloud.databricks.com"
token = "XYZ"

# COMMAND ----------

import mlflow
import os
import pandas as pd
from mlflow.tracking import MlflowClient
import requests
import json

# COMMAND ----------

# ProxyModelPyFunc function
class ProxyModelPyFunc(mlflow.pyfunc.PythonModel):

    def load_context(self, context):
        import mlflow
        target_model = "passthrough"
        os.environ["MLFLOW_TRACKING_TOKEN"] = os.environ["MLFLOW_TRACKING_TOKEN"]
        mlflow.set_tracking_uri(os.environ['MLFLOW_REGISTRY_URI'])
        self.model = mlflow.pyfunc.load_model(f"models:/{target_model}/latest")

    def predict(self, context, model_input):
        return self.model.predict(model_input)

# COMMAND ----------

# Log the model
with mlflow.start_run() as run:
    mlflow.pyfunc.log_model(
        "ProxyModel",
        python_model=ProxyModelPyFunc(),
        registered_model_name= proxy_model_name,
        pip_requirements= mlflow.pyfunc.get_model_dependencies(f"models:/{target_model}/latest", format='pip')
    )

# COMMAND ----------

# test the pyfunc
os.environ["MLFLOW_REGISTRY_URI"] = dbutils.secrets.get(scope="bilal-model-registry", key="target-host")
os.environ["MLFLOW_TRACKING_TOKEN"] = dbutils.secrets.get(scope="bilal-model-registry", key="target-token")
loaded_model = mlflow.pyfunc.load_model(f"models:/{proxy_model_name}/latest")
loaded_model.predict(pd.DataFrame([1]))

# COMMAND ----------

# Deploy the model to an endpoint
client = MlflowClient()
url = f"https://{instance}/api/2.0/serving-endpoints"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
payload = {
    "name": model_serving_endpoint_name,
    "config":{
      "served_models": [{
            "model_name": proxy_model_name,
            "model_version": client.get_registered_model(proxy_model_name).latest_versions[0].version,
            "workload_size": "Small",
            "scale_to_zero_enabled": "True",
            "environment_vars": {
              "MLFLOW_REGISTRY_URI": "{{secrets/bilal-model-registry/target-host}}",
              "MLFLOW_TRACKING_TOKEN": "{{secrets/bilal-model-registry/target-token}}",
              }

      }]
    }
}
response = requests.post(url, headers=headers, data=json.dumps(payload))

# COMMAND ----------

response.text
