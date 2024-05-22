from typing import Dict
from kubernetes.client.rest import ApiException
from kubernetes import client, config
from models.MLModel import MLModel
import os

kube_config_path = os.environ.get('KUBECONFIG')
if kube_config_path and os.path.exists(kube_config_path):
    config.load_kube_config()
else:
    config.load_incluster_config()


class MLDeployer:
    def __init__(self):
        self.apps_v1_api = client.AppsV1Api()
        self.autoscaling_v1_api = client.AutoscalingV1Api()
        self.core_v1_api = client.CoreV1Api()

    def deploy_model(self, model: MLModel) -> MLModel:
        model_name = model.name
        model_version = model.version
        model_image_url = model.image_url

        model_exposed_port = model.exposed_port

        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=f"{model_name}-{model_version}"),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={"app": f"{model_name}-{model_version}"}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": f"{model_name}-{model_version}"}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=f"{model_name}-{model_version}-container",
                                image=model_image_url,
                                ports=[client.V1ContainerPort(container_port=model_exposed_port)]
                            )
                        ]
                    )
                )
            )
        )

        try:
            api_response = self.apps_v1_api.create_namespaced_deployment(
                body=deployment, namespace="default"
            )
            print(f"Deployment created: {api_response.metadata.name}")
        except ApiException as e:
            print(f"Exception when creating deployment: {e}")
            raise

        return model

    def apply_horizontal_autoscaler(self, model: MLModel):
        model_name = model.name
        model_version = model.version
        autoscaler = client.V1HorizontalPodAutoscaler(
            api_version="autoscaling/v1",
            kind="HorizontalPodAutoscaler",
            metadata=client.V1ObjectMeta(
                name=f"{model_name}-{model_version}-autoscaler",
                labels={"app": f"{model_name}-{model_version}"},
            ),
            spec=client.V1HorizontalPodAutoscalerSpec(
                min_replicas=model.min_replicas,
                max_replicas=model.max_replicas,
                scale_target_ref=client.V1CrossVersionObjectReference(
                    api_version="apps/v1",
                    kind="Deployment",
                    name=f"{model_name}-{model_version}",
                ),
                target_cpu_utilization_percentage=80,
            ),
        )

        try:
            api_response = self.autoscaling_v1_api.create_namespaced_horizontal_pod_autoscaler(
                body=autoscaler, namespace="default"
            )
            print(f"Horizontal autoscaler created: {api_response.metadata.name}")
        except ApiException as e:
            print(f"Exception when creating HorizontalPodAutoscaler: {e}")
            raise

        return model

    def create_cluster_ip_service(self, model: MLModel):
        model_name = model.name
        model_version = model.version
        port = model.exposed_port
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name=f"{model_name}-{model_version}-service",
            ),
            spec=client.V1ServiceSpec(
                type="ClusterIP",
                selector={"app": f"{model_name}-{model_version}"},
                ports=[client.V1ServicePort(port=port, target_port=port)],
            ),
        )

        try:
            api_response = self.core_v1_api.create_namespaced_service(
                body=service, namespace="default"
            )
            print(f"ClusterIP service created: {api_response.metadata.name}")
        except ApiException as e:
            print(f"Exception when creating Service: {e}")
            raise

        return model

    def delete_model(self, model_name: str, model_version: str):
        try:
            self.apps_v1_api.delete_namespaced_deployment(
                name=f"{model_name}-{model_version}", namespace="default"
            )
            self.autoscaling_v1_api.delete_namespaced_horizontal_pod_autoscaler(
                name=f"{model_name}-{model_version}-autoscaler", namespace="default"
            )
            self.core_v1_api.delete_namespaced_service(
                name=f"{model_name}-{model_version}-service", namespace="default"
            )
        except ApiException as e:
            print(f"Exception when deleting model: {e}")
            raise


if __name__ == "__main__":
    k8s = MLDeployer()

    model_request = MLModel(
        image_url="microsoft/mlops-python",
        exposed_port=5001,
        name="mlops-python",
        version="v1"
    )

    k8s.deploy_model(model_request)
