import json
import time
import boto3


# Create an SSM client
ssm_client = boto3.client('ssm')

def lambda_handler(event, context):
    recycle_app_pool_result = []
    for data in event['Data']:
        if (data.get('PrerequisiteScript') != None):
            script_result = execute_pre_requisite_script(data['PrerequisiteScript'])

            if script_result['Status'] != "Success":
                recycle_app_pool_result.append(script_result)
                continue
        
        recycle_app_pool_result.append(send_command(data['InstanceId'], data['AppPoolName']))

    return recycle_app_pool_result

def execute_pre_requisite_script(instance_id, script_path):
    try:
        custom_script_commands = [
        f'PowerShell.exe -File {script_path}'
        ]
        
        custom_script_response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunPowerShellScript',
            Parameters={'commands': custom_script_commands}
        )

        custom_script_command_id = custom_script_response['Command']['CommandId']
        
        # Wait for the custom script to complete
        while True:
            custom_script_result = ssm_client.get_command_invocation(
                CommandId=custom_script_command_id,
                InstanceId=instance_id
            )
            
            if custom_script_result['Status'] in ['Success', 'Failed', 'TimedOut', 'Cancelled']:
                break
            
            time.sleep(5)  # Wait for 5 seconds before checking the status again
        
        return {
                'Status': custom_script_result['Status'],
                'StandardOutputContent': custom_script_result['StandardOutputContent'],
                'StandardErrorContent': custom_script_result['StandardErrorContent']
                }
    except Exception as e:
        return {
            'Status': 'Failed',
            'Error': repr(e)
        }

def send_command(instance_id, app_pool_name):
    
    try:
        document_name = 'AWS-RunPowerShellScript'
        parameters = {
            'commands': ["Restart-WebAppPool -Name '"+app_pool_name+"'"]
        }
        
        # Send the command
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName=document_name,
            Parameters=parameters
        )
        
        command_id = response['Command']['CommandId']
        
        while True:
            result = ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            
            if result['Status'] in ['Success', 'Failed', 'TimedOut', 'Cancelled']:
                break
            
            time.sleep(5)

        return {
                'Status': result['Status'],
                'StandardOutputContent': result['StandardOutputContent'],
                'StandardErrorContent': result['StandardErrorContent']
            }
    except Exception as e:
        return {
            'Status': 'Failed',
            'Error': repr(e)
        }

# Local Driver
event = {
    'Data': [{
        'InstanceId':'',
        'AppPoolName': ''
    },{
        'InstanceId':'',
        'AppPoolName': '',
        'PrerequisiteScript':''
    }],
    'PrecheckOnly': False
}

print(lambda_handler(event, None))