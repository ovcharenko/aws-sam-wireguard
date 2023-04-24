import base64
import boto3
from botocore.exceptions import ClientError
from cfnresponse import FAILED, SUCCESS, send
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


def create_keys():
    # Generate WireGuard server keys
    private_key_obj = X25519PrivateKey.generate()
    return {
        "private_key": (
            base64.b64encode(
                private_key_obj.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
            .decode("utf-8")
            .strip()
        ),
        "public_key": (
            base64.b64encode(
                private_key_obj.public_key().public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                )
            )
            .decode("utf-8")
            .strip()
        ),
    }


def create_and_upload_keys(ssm):
    keys = create_keys()

    # Store the keys in the Parameter Store
    ssm.put_parameter(
        Name="/wireguard/server/private_key",
        Type="SecureString",
        Value=keys.get("private_key"),
        Overwrite=True,
    )
    ssm.put_parameter(
        Name="/wireguard/server/public_key",
        Type="String",
        Value=keys.get("public_key"),
        Overwrite=True,
    )


def handler(event, context):
    ssm = boto3.client("ssm")

    public_key = None

    # Check if the keys already exist in the Parameter Store
    try:
        _ = ssm.get_parameter(
            Name="/wireguard/server/private_key", WithDecryption=True
        )["Parameter"]["Value"]
        public_key = ssm.get_parameter(Name="/wireguard/server/public_key")[
            "Parameter"
        ]["Value"]
    except ClientError as e:
        if e.response["Error"]["Code"] in "ParameterNotFound":
            create_and_upload_keys(ssm)
        else:
            # Send a failure response with the error message as output data
            send(event, context, FAILED, {"Error": str(e)})

    response_data = {"PublicKey": public_key}
    send(event, context, SUCCESS, response_data)
