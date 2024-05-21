from fastapi import FastAPI, HTTPException
from kubernetes import client, config
import requests
import psycopg2

from k8s.MLDeployer import MLDeployer
from models.MLModel import MLModel
import os

app = FastAPI()
k8s = MLDeployer()

# Attempt to load from environment variable first
kube_config_path = os.environ.get('KUBECONFIG')
if kube_config_path and os.path.exists(kube_config_path):
    config.load_kube_config()
else:
    config.load_incluster_config()

db_name = os.getenv('POSTGRES_DB')
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv("POSTGRES_PORT")

db_config = {
    'dbname': db_name,
    'user': db_user,
    'password': db_password,
    'host': db_host,  # This is the Kubernetes service name
    'port': db_port,
}

print(f"Database configuration: {db_config}")
@app.get("/dbx/version")
async def db_version():
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"message": "Connected to PostgreSQL", "db_version": record[0]}


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

    return {"status": "Model deployed", **model.dict()}


@app.delete("/model/{model_name}/{model_version}")
def delete_model(model_name: str, model_version: str):
    model_key = f"{model_name}:{model_version}"
    try:
        k8s.delete_model(model_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "Model deleted"}


@app.get("/model/{model_name}/{model_version}", response_model=MLModel)
async def get_model(model_name: str, model_version: str):
    model_key = f"{model_name}:{model_version}"
    model_metadata = k8s.get_model(model_key)

    return {
        **model_metadata.dict()
    }


@app.get("/")
def hello_world():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
