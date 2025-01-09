import boto3

def lambda_handler(event, context):
    secret_test_result = []
    proceedToNextStep = True

    for secret in event['TestResult']:
        test_result = rotate_secret_versions(secret['SecretName'])

        if (test_result[1] == True):
            secret_test_result.append({
                'SecretName': secret['SecretName'],
            })
            continue
        
        proceedToNextStep = False
        secret_test_result.append({
                'SecretName': secret['SecretName'],
                'ErrorMessage': test_result[2]
        })

    return {
        'Result': secret_test_result,
        'ProceedToNextStep': proceedToNextStep
    }

def rotate_secret_versions(secret):
    try :
        client = boto3.client('secretsmanager')

        metadata = client.describe_secret(SecretId=secret['SecretName'])
        current_version = None
        prev_version = None
        pending_version = None

        for version in metadata["VersionIdsToStages"]:
            if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
                current_version = version
                continue

            if "AWSPENDING" in metadata["VersionIdsToStages"][version]:
                pending_version = version
                continue

            if "AWSPREVIOUS" in metadata["VersionIdsToStages"][version]:
                prev_version = version
                continue

        if prev_version:
            client.update_secret_version_stage(
                SecretId=secret['SecretName'], 
                VersionStage="AWSPREVIOUS", 
                MoveToVersionId=current_version, 
                RemoveFromVersionId=prev_version)
        else:
            client.update_secret_version_stage(
                SecretId=secret['SecretName'], 
                VersionStage="AWSPREVIOUS", 
                MoveToVersionId=current_version)

        client.update_secret_version_stage(SecretId=secret['SecretName'], VersionStage="AWSCURRENT", MoveToVersionId=pending_version ,RemoveFromVersionId=current_version)
        client.update_secret_version_stage(SecretId=secret['SecretName'], VersionStage="AWSPENDING", RemoveFromVersionId=pending_version)
    
        return secret['SecretName'], True
    except Exception as e:
        return secret['SecretName'], False, repr(e)

# Local Driver
event = {
    'TestResult': [{
        'SecretName':'sm-mwb-l-m-sitecore_collection'
    }],
    'PrecheckOnly': False
}

print(lambda_handler(event, None))
