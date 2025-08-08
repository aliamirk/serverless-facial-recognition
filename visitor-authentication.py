# This AWS Lambda function is triggered via an API Gateway HTTP request. It takes an `objectKey` query parameter to fetch an image 
# from a specific S3 bucket, uses Amazon Rekognition to search for matching faces in the "employees" collection, 
# and retrieves employee details (first and last name) from a DynamoDB table based on the face match. 
# It returns a success response if a match is found, or an error message if the person is not recognized.



import boto3
import json

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

dynamodbTableName = '<your-table-name>'
employeeTable = dynamodb.Table(dynamodbTableName)
bucketName = '<your-bucket-name>'

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    params = event.get('queryStringParameters')
    if not params or 'objectKey' not in params:
        return buildResponse(400, {'Message': 'Missing objectKey parameter'})

    objectKey = params['objectKey']
    print(f"Looking for S3 object with key: {objectKey}")

    try:
        response = rekognition.search_faces_by_image(
            CollectionId='employees',
            Image={
                'S3Object': {
                    'Bucket': bucketName,
                    'Name': objectKey
                }
            },
            FaceMatchThreshold=85,
            MaxFaces=1
        )

        for match in response.get('FaceMatches', []):
            face_id = match['Face']['FaceId']
            confidence = match['Face']['Confidence']
            print(f"Matched FaceId: {face_id}, Confidence: {confidence}")

            result = employeeTable.get_item(Key={'rekognitionId': face_id})
            if 'Item' in result:
                item = result['Item']
                print('Employee Found:', item)
                return buildResponse(200, {
                    'Message': 'Success',
                    'firstName': item.get('firstname'),
                    'lastName': item.get('lastname')
                })

        print('No matching employee found in database')
        return buildResponse(403, {'Message': 'Person Not Found'})

    except rekognition.exceptions.InvalidImageFormatException:
        return buildResponse(400, {'Message': 'Invalid image format. Must be JPEG or PNG.'})
    except rekognition.exceptions.InvalidS3ObjectException:
        return buildResponse(404, {'Message': 'S3 object not found or not readable.'})
    except Exception as e:
        print("Unhandled exception:", str(e))
        return buildResponse(500, {'Message': 'Internal Server Error'})


def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Headers': '*'
        }
    }

    if body is not None:
        response['body'] = json.dumps(body)
    return response
