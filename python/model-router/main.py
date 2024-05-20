from fastapi import FastAPI, HTTPException
from typing import Dict
from k8s.MLDeployer import MLDeployer
from models.MLModel import MLModel

app = FastAPI()
k8s = MLDeployer()

@app.post("/models")
async def create_model(model: MLModel):  
    try:
        model = k8s.deploy_model(model) # Deploy the model with a single pod  
        model = k8s.apply_horizontal_autoscaler(model) # Create the horizontal autoscaler
        model = k8s.create_cluster_ip_service(model) # Create the ClusterIP service

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status" : "Model deployed", **model.model_dump()}


@app.get("/model/{model_key}", response_model=MLModel)
async def get_model(model_key: str):
    model_metadata = k8s.get_model(model_key)
    
    return {
        **model_metadata
    }

@app.get("/")
def hello_world():
    return {"Hello": "World"}
