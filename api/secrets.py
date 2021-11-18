from typing import Tuple

from ..connectors.secrets import get_project_secrets, set_project_secrets, get_project_hidden_secrets

from ...shared.utils.restApi import RestResource
from ...shared.utils.api_utils import build_req_parser


class SecretsAPI(RestResource):  # pylint: disable=C0111
    post_rules = (
        dict(name="secrets", type=dict, required=True, default=None, location="json"),
    )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._parser_post = build_req_parser(rules=self.post_rules)

    def get(self, project_id: int) -> Tuple[list, int]:  # pylint: disable=R0201,C0111
        # Check project_id for validity
        project = self.rpc.project_get_or_404(project_id)
        # Get secrets
        secrets_dict = get_project_secrets(project.id)
        resp = []
        for key in secrets_dict.keys():
            resp.append({"name": key, "secret": "******"})

        for key in get_project_hidden_secrets(project.id):
            resp.append({"name": key, "secret": "******", 'is_hidden': True})

        return resp, 200

    def post(self, project_id: int) -> Tuple[dict, int]:  # pylint: disable=C0111
        data = self._parser_post.parse_args()
        # Check project_id for validity
        project = self.rpc.project_get_or_404(project_id)
        # Set secrets
        set_project_secrets(project.id, data["secrets"])
        return {"message": f"Project secrets were saved"}, 200


class SecretsAPIBulkDelete(RestResource):  # pylint: disable=C0111

    post_rules = (
        dict(name="secrets", type=set, required=True, default={}, location="json"),
    )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._parser_post = build_req_parser(rules=self.post_rules)

    def post(self, project_id: int) -> Tuple[dict, int]:  # pylint: disable=C0111
        project = self.rpc.project_get_or_404(project_id)
        data = self._parser_post.parse_args()
        secrets = get_project_secrets(project.id)
        for secret in data.get('secrets', []):
            try:
                del secrets[secret]
            except KeyError:
                ...
        set_project_secrets(project.id, secrets)
        return {"message": "deleted"}, 200