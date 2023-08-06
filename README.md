# Model-Proxy-Databricks-Serving


This repository demonstrates how to retrieve an MLflow model during runtime, or after creating the container. This is particularly helpful in scenarios where there is a need to rapidly update an endpoint with a recently retrained model. 

_Please be aware that when updating the mode, the previous container with dependencies will be utilized. If there are any changes in the dependencies of the new model, the container must be recreated accordingly._

<b>Terminologies</b>

- **ProxyModel** is the model that the container is built for.
- **TargetModel** is the model that is invoked by the ProxyModel.

<b>Pre-reading</b>

This example uses the below two concepts. Please read and review the following articles:
- https://docs.databricks.com/en/machine-learning/model-serving/deploy-custom-models.html
- https://docs.databricks.com/en/machine-learning/model-serving/store-env-variable-model-serving.html#

<b>Getting Started</b>

1. To deploy the proxy model and target model to the endpoint, begin by opening the ProxyModel.py file. Fill in the necessary parameters located at the beginning of the notebook. Running the file will initiate the deployment process
2. To update the target model on the endpoint, simply make changes to the target model and then run UpdateDeploymentPipeline.py. This process should be quite fast as it only requires updating the model without recreating the docker container.
