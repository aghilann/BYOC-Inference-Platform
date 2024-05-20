from fastapi import FastAPI, HTTPException
from kubernetes import config

from k8s.MLDeployer import MLDeployer
from models.MLModel import MLModel

app = FastAPI()
k8s = MLDeployer()

config.load_kube_config()


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
        **model_metadata
    }


@app.get("/")
def hello_world():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
