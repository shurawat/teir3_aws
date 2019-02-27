import boto3


class ClientLocator:
    def __init__(self, client):
        self._client = boto3.client(client, region_name="us-east-1")

    def get_client(self):
        return self._client


class Client(ClientLocator):
    def __init__(self, client):
        super().__init__(client)
