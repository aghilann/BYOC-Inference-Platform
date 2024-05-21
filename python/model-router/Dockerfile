FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Install Kubernetes Client
RUN pip install kubernetes

# Install other requirements
RUN pip install --no-cache-dir -r requirements.txt

# Do not copy kube-config inside the cluster
# It's assumed the cluster will provide this automatically

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
