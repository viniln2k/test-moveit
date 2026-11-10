import json

import boto3


def get_secret(secret_name):
    """

    :param secret_name:
    :return:
    """
    get_secret_value_response = ""
    try:
        secrets_manager = boto3.client('secretsmanager')

        get_secret_value_response = secrets_manager.get_secret_value(
            SecretId=secret_name
        )

    except Exception as e:
        raise
    return get_secret_value_response


def get_secret_value(secret_response, secret_key):
    """

    :param secret_response:
    :param secret_key:
    :return:
    """
    secret_value = ""
    try:
        if 'SecretString' in secret_response:
            secret = secret_response['SecretString']
            if secret is not None:
                secret_value = json.loads(secret)[secret_key]
    except Exception:
        raise
    return secret_value
