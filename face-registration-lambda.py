# This Lambda function is triggered by an image upload in an S3 bucket.
# It uses Rekognition to generate face vectors and stores the face ID in a DynamoDB table.
# The image name (key) is expected to be the first and last name. e.g., First_Last.png

import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

dynamodbTableName = '<your-table-name>'
employeeTable = dynamodb.Table(dynamodbTableName)  

def lambda_handler(event, context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try:
        response = index_employee_image(bucket, key)
        print(response)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200: 
            faceId = response['FaceRecords'][0]['Face']['FaceId']

            filename = key.split('.')[0]  # remove extension
            name_parts = filename.split('_')
            firstname = name_parts[0]
            lastname = name_parts[1] if len(name_parts) > 1 else ''

            register_employee(faceId, firstname, lastname) 
        return response

    except Exception as e:
        print(e)
        print(f"Error formatting employee image {key} from bucket {bucket}.")
        raise e

def index_employee_image(bucket, key):
    response = rekognition.index_faces(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        CollectionId="<your-collection-id>",
        DetectionAttributes=['DEFAULT']
    )
    return response

def register_employee(faceId, firstname, lastname):
    employeeTable.put_item(
        Item={
            'rekognitionId': faceId,
            'firstname': firstname,
            'lastname': lastname
        }
    )