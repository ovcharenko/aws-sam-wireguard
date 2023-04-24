from unittest.mock import MagicMock, patch

import boto3
import pytest
import requests
from botocore.exceptions import ClientError

from keys_generate import create_keys, handler


@pytest.fixture(scope="session")
def event():
    # Create the event dictionary
    return {
        "RequestType": "Create",
        "ResponseURL": "https://cloudformation-response.example.com/",
        "StackId": "my-stack-id",
        "RequestId": "my-request-id",
        "LogicalResourceId": "my-logical-resource-id",
    }


@pytest.fixture(scope="session")
def context():
    # Create a mock context object
    context = MagicMock()
    context.log_stream_name = "my-log-stream"

    return context


@pytest.fixture(scope="session")
def keys():
    return create_keys()


def test_handler_with_existing_keys(event, context, keys):
    # Mock the SSM client
    ssm_mock = MagicMock()
    ssm_mock.get_parameter.side_effect = [
        {
            "Parameter": {
                "Name": "/wireguard/server/private_key",
                "Type": "SecureString",
                "Value": keys.get("private_key"),
            }
        },
        {
            "Parameter": {
                "Name": "/wireguard/server/public_key",
                "Type": "String",
                "Value": keys.get("public_key"),
            }
        },
    ]

    # Patch the Boto3 client creation function to return the mock
    with patch.object(boto3, "client") as mock_client, patch.object(
        requests, "put"
    ) as put_mock:
        put_mock.return_value.status_code = 200
        put_mock.return_value.text = ""
        mock_client.return_value = ssm_mock

        # Call the function to be tested
        handler(event, context)

    # Check that the SSM mock was called correctly
    ssm_mock.get_parameter.assert_any_call(
        Name="/wireguard/server/private_key", WithDecryption=True
    )
    ssm_mock.get_parameter.assert_any_call(Name="/wireguard/server/public_key")
    ssm_mock.put_parameter.assert_not_called()


def test_handler_with_new_keys(event, context, keys):
    # Mock the SSM client
    ssm_mock = MagicMock()
    ssm_mock.get_parameter.side_effect = [
        ClientError({"Error": {"Code": "ParameterNotFound"}}, "get_parameter"),
        {
            "Parameter": {
                "Name": "/wireguard/server/public_key",
                "Type": "String",
                "Value": keys.get("public_key"),
            }
        },
    ]
    ssm_mock.put_parameter.return_value = {}

    # Patch the Boto3 client creation function to return the mock
    with patch.object(boto3, "client") as mock_client, patch.object(
        requests, "put"
    ) as put_mock:
        put_mock.return_value.status_code = 200
        put_mock.return_value.text = ""
        mock_client.return_value = ssm_mock

        # Call the function to be tested
        handler(event, context)

    # Check that the SSM mock was called correctly
    ssm_mock.get_parameter.assert_called_with(
        Name="/wireguard/server/private_key", WithDecryption=True
    )
