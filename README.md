# BYOC-Inference-Platform

When inside model-router directory, run these commands to update the image

# Tag the image

docker tag model-router aghilann/model-router:latest

# Log in to Docker Hub

docker login

# Push the image

docker push aghilann/model-router:latest

curl -X POST "http://localhost:8000/models" -H "Content-Type: application/json" -d '{
"image_url": "microsoft/mlops-python",
"exposed_port": 5001,
"name": "mlops-python",
"version": "v2"
}'
