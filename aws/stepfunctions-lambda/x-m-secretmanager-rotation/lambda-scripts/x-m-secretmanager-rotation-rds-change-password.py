import boto3
import pymssql
import json
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    secret_test_result = []
    proceedToNextStep = True

    for secret in event['TestResult']:
        
        test_result = change_sql_user_password(secret['SecretName'])

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
        'Result': event['TestResult'],
        'ProceedToNextStep': proceedToNextStep
    }

def get_secret_value(secret_name, version_stage):
    # Create a Secrets Manager client
    client = boto3.client('secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name,
            VersionStage=version_stage
        )
    except ClientError as e:
        raise Exception("Unable to retrieve secret: " + str(e))
    
    return json.loads(get_secret_value_response['SecretString'])

def change_sql_user_password(secret_name):
    # Retrieve the current and pending passwords from Secrets Manager
    current_secret = get_secret_value(secret_name, "AWSCURRENT")
    pending_secret = get_secret_value(secret_name, "AWSPENDING")
    
    try:
        # Connect to the SQL Server database
        connection = pymssql.connect(
            server=current_secret['host'],
            user=current_secret['username'],
            password=current_secret['password'],
            database=current_secret['dbname']
        )
        cursor = connection.cursor()
        
        # Change the password for the user themselves
        cursor.execute(f"ALTER LOGIN [{current_secret['username']}] WITH PASSWORD = '{pending_secret['password']}';")
        connection.commit()
        
        return secret_name, True
    except pymssql.Error as e:
        return secret_name, False, repr(e)
    finally:
        connection.close()

# Local Driver
event = {
    'TestResult': [{
        'SecretName':'sm-mwb-l-m-sitecore_collection'
    }],
    'PrecheckOnly': False
}

print(lambda_handler(event, None))