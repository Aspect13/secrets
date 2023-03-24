from typing import Tuple

from flask import request

from tools import api_tools, VaultClient


class ProjectAPI(api_tools.APIModeHandler):  # pylint: disable=C0111
    def get(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=R0201,C0111
        # Check project_id for validity
        project = self.module.context.rpc_manager.call.project_get_or_404(project_id)
        vault_client = VaultClient.from_project(project)
        # Get secret
        secrets = vault_client.get_project_secrets()
        _secret = secrets.get(secret) or vault_client.get_project_hidden_secrets().get(secret)
        return {"secret": _secret}, 200

    def post(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=C0111
        data = request.json
        # Check project_id for validity
        project = self.module.context.rpc_manager.call.project_get_or_404(project_id)
        vault_client = VaultClient.from_project(project)
        # Set secret
        secrets = vault_client.get_project_secrets()
        secrets[secret] = data["secret"]
        vault_client.set_project_secrets(secrets)
        return {"message": "Project secret was saved"}, 200

    def put(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=C0111
        data = request.json
        # Check project_id for validity
        project = self.module.context.rpc_manager.call.project_get_or_404(project_id)
        vault_client = VaultClient.from_project(project)
        # Set secret
        secrets = vault_client.get_project_secrets()
        try:
            del secrets[data['secret']['old_name']]
        except KeyError:
            return {"message": "Project secret was not found"}, 404
        secrets[secret] = data["secret"]['value']
        vault_client.set_project_secrets(secrets)
        return {"message": "Project secret was updated"}, 200

    def delete(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=C0111
        project = self.module.context.rpc_manager.call.project_get_or_404(project_id)
        vault_client = VaultClient.from_project(project)
        secrets = vault_client.get_project_secrets()
        if secret in secrets:
            del secrets[secret]
        vault_client.set_project_secrets(secrets)
        return {"message": "deleted"}, 204


class AdminAPI(api_tools.APIModeHandler):  # pylint: disable=C0111
    def get(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=R0201,C0111
        vault_client = VaultClient()
        # Get secret
        secrets = vault_client.get_project_secrets()
        # _secret = secrets.get(secret) or vault_client.get_project_hidden_secrets().get(secret)
        _secret = secrets.get(secret)
        return {"secret": _secret}, 200

    def post(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=C0111
        data = request.json
        # Set secret
        vault_client = VaultClient()
        secrets = vault_client.get_project_secrets()
        secrets[secret] = data["secret"]
        vault_client.set_project_secrets(secrets)
        return {"message": "Project secret was saved"}, 200

    def put(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=C0111
        data = request.json
        # Set secret
        vault_client = VaultClient()
        secrets = vault_client.get_project_secrets()
        try:
            del secrets[data['secret']['old_name']]
        except KeyError:
            return {"message": "Project secret was not found"}, 404
        secrets[secret] = data["secret"]['value']
        vault_client.set_project_secrets(secrets)
        return {"message": "Project secret was updated"}, 200

    def delete(self, project_id: int, secret: str) -> Tuple[dict, int]:  # pylint: disable=C0111
        vault_client = VaultClient()
        secrets = vault_client.get_project_secrets()
        if secret in secrets:
            del secrets[secret]
        vault_client.set_project_secrets(secrets)
        return {"message": "deleted"}, 204


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>/<string:secret>'
    ]

    mode_handlers = {
        'default': ProjectAPI,
        'administration': AdminAPI,
    }
