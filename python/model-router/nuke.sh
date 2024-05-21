#!/bin/bash

# Get all Deployments, Services, and HPAs
deployments=$(kubectl get deployments -o name)
services=$(kubectl get services -o name)
hpas=$(kubectl get hpa -o name)

# Delete Deployments
for deployment in $deployments; do
    if [[ $deployment != "service/kubernetes" ]]; then  # Exclude kubernetes service
        kubectl delete $deployment
    fi
done

# Delete Services
for service in $services; do
    if [[ $service != "service/kubernetes" ]]; then  # Exclude kubernetes service
        kubectl delete $service
    fi
done

# Delete HPAs
for hpa in $hpas; do
    kubectl delete $hpa
done