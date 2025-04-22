import json
import boto3
import os

secretsmanager_client = boto3.client('secretsmanager')

def lambda_handler(event, context):
    error_result = []
    proceedToNextStep = True

    for secret in event['Result']:
        try:
            create_new_secret_version(secret['SecretName'])
        except Exception as e:
            proceedToNextStep = False
            error_result.append(repr(e))

    return {
        'Result': event['Result'],
        'ProceedToNextStep': proceedToNextStep,
        'ErrorMessage': error_result
    }

def create_new_secret_version(secret_name):
    client = boto3.client('secretsmanager')

    response = client.get_secret_value(SecretId=secret_name) 
    secret_string = response['SecretString'] 
    secret = json.loads(secret_string)

    secret['password'] = get_random_password() 
    secret_string = json.dumps(secret)

    response = client.put_secret_value(
        SecretId=secret_name, 
        SecretString=secret_string, 
        VersionStages=['AWSPENDING'] 
    ) 
    
    return response

def get_random_password():
    passwd = secretsmanager_client.get_random_password(
        ExcludeCharacters=os.environ.get('EXCLUDE_CHARACTERS', '/@"\'\\'),
        PasswordLength=int(os.environ.get('PASSWORD_LENGTH', 32)),
        ExcludeNumbers=get_environment_bool('EXCLUDE_NUMBERS', False),
        ExcludePunctuation=get_environment_bool('EXCLUDE_PUNCTUATION', False),
        ExcludeUppercase=get_environment_bool('EXCLUDE_UPPERCASE', False),
        ExcludeLowercase=get_environment_bool('EXCLUDE_LOWERCASE', False),
        RequireEachIncludedType=get_environment_bool('REQUIRE_EACH_INCLUDED_TYPE', True)
    )
    return passwd['RandomPassword']

def get_environment_bool(variable_name, default_value):
    variable = os.environ.get(variable_name, str(default_value))
    return variable.lower() in ['true', '1', 'y', 'yes']

# Local Driver
event = {
    'TestResult': [{
        'SecretName':'sm-mwb-l-m-sc'
    }],
    'PrecheckOnly': False
}

print(lambda_handler(event, None))