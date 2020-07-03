import boto3
import json
from botocore.exceptions import NoCredentialsError

AWS_ACCESS_KEY_ID = 'AKIA4RLFJBNMP3ZKUY6C'
AWS_SECRET_ACCESS_KEY = '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'
REGION_NAME = 'us-east-2'
BUCKET_NAME = 'swe599-bucket'
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(BUCKET_NAME)

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name=REGION_NAME)

rekognition = boto3.client('rekognition', aws_access_key_id=AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION_NAME)


def upload_file_to_s3(file):
    try:
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            file.filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    return "{}{}".format(S3_LOCATION, file.filename)


def get_faces(photo_name):
    print(photo_name)
    response = rekognition.detect_faces(Image={'S3Object': {'Bucket': BUCKET_NAME, 'Name': photo_name}},
                                        Attributes=['ALL'])
    print('Detected faces for ' + photo_name)
    print('Number of faces: ' + str(len(response['FaceDetails'])))
    i = 1
    for faceDetail in response['FaceDetails']:
        faceDetail['Mood'] = {
            "Confidence": faceDetail['Emotions'][0]['Confidence'],
            "Type": faceDetail['Emotions'][0]['Type']
        }
        for emotion in faceDetail['Emotions']:
            if emotion['Confidence'] > faceDetail['Mood']['Confidence']:
                faceDetail['Mood'] = {
                    "Confidence": emotion['Confidence'],
                    "Type": emotion['Type']
                }
        faceDetail['face_name'] = "Face " + str(i)
        i = i + 1
        faceDetail['BoundingBox']['Height'] = faceDetail['BoundingBox']['Height'] * 100
        faceDetail['BoundingBox']['Width'] = faceDetail['BoundingBox']['Width'] * 100
        faceDetail['BoundingBox']['Left'] = faceDetail['BoundingBox']['Left'] * 100
        faceDetail['BoundingBox']['Top'] = faceDetail['BoundingBox']['Top'] * 100
        faceDetail['css_style'] = "position: absolute; top: " + str(faceDetail['BoundingBox']['Top']) + "%; left: " + \
                                  str(faceDetail['BoundingBox']['Left']) + "%; " \
                                                                      "height: " + str(faceDetail['BoundingBox'][
                                      'Height']) + "%; width: " + str(faceDetail['BoundingBox'][
                                      'Width']) + "%; border: 2px solid rgba(" \
                                                 "255, 255, 255, 0.690196); border-top-left-radius: 3%; border-top-right-radius: 3%; border-bottom-right-radius: 3%; border-bottom-left-radius: 3%; "
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
        print('Here are the other attributes:')
        print(json.dumps(faceDetail, indent=4, sort_keys=True))
    return response['FaceDetails']

def get_objects(photo_name):
    response = rekognition.detect_labels(Image={'S3Object': {'Bucket': BUCKET_NAME, 'Name': photo_name}})
    for label in response['Labels']:
        for instance in label['Instances']:
            instance['css_style'] = "position: absolute; top: " + str(instance['BoundingBox']['Top'] * 100) + "%; left: " + \
                                  str(instance['BoundingBox']['Left'] * 100) + "%; " \
                                                                      "height: " + str(instance['BoundingBox'][
                                      'Height'] * 100) + "%; width: " + str(instance['BoundingBox'][
                                      'Width'] * 100) + "%; border: 2px solid rgba(" \
                                                 "255, 255, 255, 0.690196); border-top-left-radius: 3%; border-top-right-radius: 3%; border-bottom-right-radius: 3%; border-bottom-left-radius: 3%; "
    print('Detected labels for ' + photo_name)
    print(json.dumps(response['Labels']))
    return response['Labels']
