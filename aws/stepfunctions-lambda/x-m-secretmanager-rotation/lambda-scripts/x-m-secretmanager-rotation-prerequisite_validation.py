import json
import boto3

def lambda_handler(event, context):
    print("x-m-secretmanager-rotation-prerequisite_validation is running")
    
    prefix = None
    preCheck = True
    proceedToNextStep = True

    try:
        prefix = event['SecretManagerPrefix']
    except:
        pass

    try:
        preCheck = event['PrecheckOnly']
    except:
        pass

    if (prefix == None or prefix == ""):
        return {
            'Message': 'Secret Manager Prefix is not set',
            'ProceedToNextStep': False,
            'PrecheckOnly': preCheck
        }

    secrets = get_secrets(prefix)

    if (secrets == None or len(secrets) == 0):
        return {
            'Message': 'Secret with prefix ' + prefix + ' is not found',
            'ProceedToNextStep': False,
            'PrecheckOnly': preCheck
        }

    print("Total Secret:", len(secrets))
    print("Secrets:", secrets)

    secret_test_result = []
    for secret in secrets:
        test_result = test_secret(secret)

        if (test_result[1] == True):
           
            secret_test_result.append({
                'SecretName': secret['SecretName'],
                'RowIssueFlag': False,
            })
            continue
        
        proceedToNextStep = False
        secret_test_result.append({
                'SecretName': secret['SecretName'],
                'RowIssueFlag': True,
                'ErrorMessage': test_result[2]
        })


    return {
        'TestRes': secret_test_result,
        'ProceedToNextStep': proceedToNextStep,
        'PrecheckOnly': preCheck
    }

def get_secrets(prefix):
    secretsmanager_client = boto3.client('secretsmanager')
    
    try:
        response = secretsmanager_client.list_secrets()
        all_secrets = response['SecretList']
        
        secrets = []
        for secret in all_secrets:
            secret_name = secret['Name']

            if secret_name.startswith(prefix) == False:
                continue

            get_secret_value_response = secretsmanager_client.get_secret_value(SecretId=secret_name)
            secret_json = json.loads(get_secret_value_response['SecretString'])
            secret_json['SecretName'] = secret_name;

            secrets.append(secret_json)

        return secrets
    except Exception as e:
        return None

# To Be Working On
def test_secret(secret):
    test_result = []
    test_result_sample = {}
    try:
        return secret['SecretName'], True
    except:
        return secret['SecretName'], False, "ERROR MESSAGE"

# Local Driver
event = {
    'SecretManagerPrefix': 'sm-',
    'PrecheckOnly': False
}

print(lambda_handler(event, None))