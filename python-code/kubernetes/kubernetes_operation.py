import argparse
import logging
from dataclasses import dataclass
from typing import List, Tuple

from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes_base import KubernetesOperationBase


@dataclass
class PodOperation(KubernetesOperationBase):
    def __post_init__(self):
        self.client_instance = client.CoreV1Api()

    def create_resource(self) -> None:
        return None

    def delete_resource(self, name: str = "default", namespace: str = "default") -> bool:
        try:
            self.client_instance.delete_namespaced_pod(name, namespace)
            return True
        except ApiException as e:
            logging.error("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)
            return False

    def list_resource(self, namespace: str = "default", label_selector: str = "") -> List[dict]:
        namespace_pod_status_list = list()
        try:
            ret = self.client_instance.list_namespaced_pod(
                namespace, watch=False, label_selector=label_selector)
            for i in ret.items:
                try:
                    if not i.status.container_statuses:
                        state = i.status.phase
                        started_at = ""
                    else:
                        if i.status.container_statuses[0].state.running:
                            state = "running"
                            started_at = str(
                                i.status.container_statuses[0].state.running.started_at)
                        elif i.status.container_statuses[0].state.waiting:
                            state = "waiting"
                            started_at = str(
                                i.status.container_statuses[0].state.waiting.started_at)
                        else:
                            state = i.status.container_statuses[0].state.terminated.reason
                            started_at = str(
                                i.status.container_statuses[0].state.terminated.started_at)
                    namespace_pod_status_list.append(
                        {
                            "name": i.metadata.name,
                            "namespace": i.metadata.namespace,
                            "state": state,
                            "started_at": started_at,
                        }
                    )
                except Exception as e:
                    logging.error(str(e))
                    continue
            return namespace_pod_status_list
        except ApiException as e:
            logging.error("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
            return namespace_pod_status_list


@dataclass
class JobOperation(KubernetesOperationBase):
    def __post_init__(self):
        self.client_instance = client.BatchV1Api()

    def create_resource(self, namespace: str = "default", body: dict = {}) -> bool:
        try:
            self.client_instance.create_namespaced_job(namespace=namespace, body=body)
            return True
        except ApiException as e:
            logging.error("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)
            return False

    def list_resource(self, namespace: str = "default", label_selector: str = "") -> Tuple[bool, list]:
        try:
            api_response = self.client_instance.list_namespaced_job(
                namespace=namespace, label_selector=label_selector
            )
            if not api_response.items:
                return (True, [])

            ret = list()
            for item in api_response.items:
                job_name = item.metadata.name

                ret.append(
                    {
                        "job_name": job_name,
                        "active": item.status.active,
                        "failed": item.status.failed,
                        "succeeded": item.status.succeeded,
                        "pods": [
                            {
                                "type": con.type,
                                "status": con.status,
                                "reason": con.reason,
                            }
                            for con in item.status.conditions
                        ]
                        if item.status.conditions
                        else [],
                    }
                )
            return (True, ret)
        except ApiException as e:
            logging.error("Exception when calling BatchV1Api->list_namespaced_job: %s\n" % e)
            return (False, [str(e)])

    def delete_resource(self, namespace: str = "default", name: str = "default") -> bool:
        try:
            self.client_instance.delete_namespaced_job(name=name, namespace=namespace)
            return True
        except ApiException as e:
            logging.error("Exception when calling BatchV1Api->delete_namespaced_job: %s\n" % e)
            return False


@dataclass
class DeploymentOperation(KubernetesOperationBase):
    def __post_init__(self):
        self.client_instance = client.AppsV1Api()

    def create_resource(self, body: dict = {}, namespace: str = "default") -> bool:
        try:
            self.client_instance.create_namespaced_deployment(
                namespace=namespace, body=body)
            return True
        except ApiException as e:
            logging.error("Exception when calling AppsV1Api->create_namespaced_deployment: %s\n" % e)
            return False

    def list_resource(self, namespace: str = "default", label_selector: str = "") -> list:
        ret = list()
        try:
            api_response = self.client_instance.list_namespaced_deployment(
                namespace=namespace, label_selector=label_selector
            )
            if not api_response.items:
                return ret

            ret = list()
            for item in api_response.items:
                deployment_name = item.metadata.name
                ret.append(deployment_name)
            return ret
        except ApiException as e:
            logging.error("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)
            return ret

    def delete_resource(self, namespace: str = "default", name: str = "") -> bool:
        try:
            self.client_instance.delete_namespaced_deployment(
                name=name, namespace=namespace)
            return True
        except ApiException as e:
            logging.error("Exception when calling AppsV1Api->delete_namespaced_deployment: %s\n" % e)
            return False


@dataclass
class NodeOperation(KubernetesOperationBase):
    def __post_init__(self):
        self.client_instance = client.CoreV1Api()

    def create_resource(self) -> None:
        return None

    def delete_resource(self) -> None:
        return None

    def list_resource(self, namespace: str = "default", label_selector: str = "") -> List[dict]:
        node_condition_list = list()
        try:
            node_list_obj = self.client_instance.list_node(label_selector=label_selector)
            for node in node_list_obj.items:
                temp = dict()
                temp["name"] = node.metadata.name
                if "node-role.kubernetes.io/master" in list(node.metadata.labels):
                    node_role = "Master"
                else:
                    node_role = "Node"
                temp["role"] = node_role
                for condition in node.status.conditions:
                    temp[condition.type] = condition.status
                node_condition_list.append(temp)
        except ApiException as e:
            logging.error("Exception when calling CoreV1Api->list_node: %s\n" % e)
        return node_condition_list


def main():
    parser = argparse.ArgumentParser(description="tool for access kubernetes resource")
    parser.add_argument("--namespace", type=str)
    parser.add_argument("--resource", type=str)
    parser.add_argument("--operation", type=str)
    parser.add_argument("--label", type=str)
    args = parser.parse_args()
    operation = args.operation
    namespace = args.namespace
    resource = args.resource
    label_selector = args.label

    if not operation or operation not in ["list", "delete", "create"]:
        logging.error(
            "please specify the right operation using --operation, the supported operations are [list delete create]")
        exit(0)

    if not namespace:
        logging.error("please specify namespace using --namespace")
        exit(0)

    if not resource or resource not in ["pod", "job", "deployment", "node"]:
        logging.error(
            "please specify the right resource using --resource, the supported operations are [pod job deployment]")
        exit(0)

    if resource == "pod":
        instance = PodOperation()
    elif resource == "job":
        instance = JobOperation()
    elif resource == "deployment":
        instance = DeploymentOperation()
    else:
        instance = NodeOperation()

    if operation == "list":
        instance.list_resource(namespace=namespace, label_selector=label_selector)
    elif operation == "delete":
        pass
    else:
        pass


if __name__ == "__main__":
    main()
