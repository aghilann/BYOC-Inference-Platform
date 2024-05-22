from fastapi import FastAPI, HTTPException
from kubernetes import client, config
import requests
import psycopg2
from k8s.MLDeployer import MLDeployer
from models.Database import Database
from models.MLModel import MLModel
from models.MLModelPersistence import MLModelPersistence
import os

app = FastAPI()
k8s = MLDeployer()

# Attempt to load from environment variable first
kube_config_path = os.environ.get('KUBECONFIG')
if kube_config_path and os.path.exists(kube_config_path):
    config.load_kube_config()
else:
    config.load_incluster_config()

db = Database.from_env()
ml_persistence = MLModelPersistence(db)

@app.get("/db/version")
async def get_db_version():
    version = db.db_version()
    return {"message": "Connected to PostgreSQL", "db_version": version}

@app.post("/model")
async def create_model(model: MLModel):
    try:
        model = k8s.deploy_model(model)  # Deploy the model with a single pod
        model = k8s.apply_horizontal_autoscaler(model)  # Create the horizontal autoscaler
        model = k8s.create_cluster_ip_service(model)  # Create the ClusterIP service

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    ml_persistence.save(model)
    return {"status": "Model deployed", **model.dict()}


@app.delete("/model/{model_name}/{model_version}")
def delete_model(model_name: str, model_version: str):
    try:
        k8s.delete_model(model_name, model_version)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        ml_persistence.delete(model_name, model_version)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": "Model deleted"}


@app.get("/model/{model_name}/{model_version}", response_model=MLModel)
async def get_model(model_name: str, model_version: str):
    model: MLModel
    try:
        model = ml_persistence.get(model_name, model_version)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "status": "Model found",
        **model.dict()
    }


@app.get("/")
def hello_world():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


"""
@app.get("/test2")
def test():
    service_name = "nginx-v1-service"
    url = f"http://{service_name}/"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx)

        # Print the response
        print(f"Response from {url}:")
        print(response.text)

        return {"status_code": response.status_code, "response": response.text}

    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        return {"error": str(e)}
"""