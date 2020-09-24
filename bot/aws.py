import os
import pickle
import boto3

ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_ACCESS_KEY = os.environ['SECRET_ACCESS_KEY']

aws_s3 = boto3.client(
    's3',
    aws_access_key_id = ACCESS_KEY,
    aws_secret_access_key = SECRET_ACCESS_KEY
)


try:
    with open('simpnotes.pickle', 'wb') as f:
        aws_s3.download_fileobj('bot-bez-bot-bucket', 'simpnotes.pickle', f)

    with open('simpnotes.pickle', 'rb') as handle:
        simpnotes = pickle.load(handle)
except:
        simpnotes = {}


def s3_sync(data):
    with open('simpnotes.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    aws_s3.upload_file('simpnotes.pickle', 'bot-bez-bot-bucket', 'simpnotes.pickle')
