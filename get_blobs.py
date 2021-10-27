from google.cloud import storage
import os

def get_blob(bucket_name, source_file_name, destination_blob_name):
    """Retrieve file from the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

if __name__ == "__main__":
    test_pat = 'a40013'
    file_path = os.path.join("train_wave", test_pat)
    bucket_name = 'physionet_2009'
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = [i for i in bucket.list_blobs() if test_pat in i.name]
    blobs[0].download_to_filename("blob_test")
