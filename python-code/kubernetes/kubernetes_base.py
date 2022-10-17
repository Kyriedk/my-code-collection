from abc import ABC, abstractmethod

from kubernetes import config


class KubernetesOperationBase(ABC):
    """
    This the kubernetes operation base layer.
    All kubernetes resource operation inherit from it.
    All operation must implement these methods.
    """
    config.load_kube_config()

    @abstractmethod
    def create_resource(self) -> None:
        """
        create kubernetes resources through kubernetes api
        """

    def list_resource(self) -> None:
        """
        list kubernetes resources through kubernetes api
        """

    def delete_resource(self) -> None:
        """
        delete kubernetes resources through kubernetes api
        """
