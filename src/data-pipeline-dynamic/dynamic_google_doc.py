import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone

# Load your Google service account credentials from environment variables
SERVICE_ACCOUNT_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Define the Google Doc ID from the URL
DOC_ID = "1qBfsiK-NNe_dMIsShMSiJe5_Qsc2tmYJMSVzbsMw0RI"


# Authenticate and build the Google Docs and Drive API services using the service account
def authenticate_gdocs_gdrive_api():
    try:
        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_CREDENTIALS,
            scopes=[
                "https://www.googleapis.com/auth/documents.readonly",
                "https://www.googleapis.com/auth/drive.readonly",
            ],
        )

        docs_service = build("docs", "v1", credentials=credentials)
        drive_service = build("drive", "v3", credentials=credentials)

        return docs_service, drive_service
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        return None, None


# Fetch the Google Doc content
def fetch_google_doc_content(doc_id, service):
    try:
        # Request the Google Docs content
        document = service.documents().get(documentId=doc_id).execute()

        # Extract the title and body content
        title = document.get("title")
        content = document.get("body").get("content")

        # Initialize an empty string to hold the content text
        doc_text = ""

        # Loop through the elements in the content and extract text
        for element in content:
            if "paragraph" in element:
                for run in element["paragraph"]["elements"]:
                    if "textRun" in run:
                        doc_text += run["textRun"]["content"]

        # Return the title and text
        return title, doc_text
    except Exception as e:
        print(f"Error fetching document: {e}")
        return None, None


# Fetch the last modified time of the Google Doc using Google Drive API
def fetch_last_modified_time(doc_id, drive_service):
    try:
        file_metadata = (
            drive_service.files().get(fileId=doc_id, fields="modifiedTime").execute()
        )
        modified_time = file_metadata.get("modifiedTime")
        if modified_time:
            # Parse the ISO format from Google (which is in UTC)
            modified_datetime = datetime.fromisoformat(
                modified_time.replace("Z", "+00:00")
            ).astimezone(timezone.utc)

            # Format the timestamp to the desired format "YYYY-MM-DDTHH:MM:SSZ"
            return modified_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            return None

    except Exception as e:
        print(f"Error fetching last modified time: {e}")
        return None


# Main function to process the Google Doc content and create the big string with metadata
def main():
    # Authenticate the Google Docs and Drive API using the service account
    docs_service, drive_service = authenticate_gdocs_gdrive_api()
    if docs_service is None or drive_service is None:
        return

    # Fetch the Google Doc content
    title, content = fetch_google_doc_content(DOC_ID, docs_service)

    # Fetch the last modified time from Google Drive API
    last_modified_time = fetch_last_modified_time(DOC_ID, drive_service)

    if title and content:
        print(f"Title: {title}\n")
        print(f"Content:\n{content}")

        # Generate the big_string by concatenating title and content
        big_string = f"Title: {title}\n\nContent:\n{content}"

        # Metadata for the new JSON
        metadata = {
            "last_modified": last_modified_time,  # Use the actual modified time if available
            "scraped_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),  # Current time in UTC formatted
            "word_count": len(big_string.split()),  # Count of words in big_string
            "url": f"https://docs.google.com/document/d/{DOC_ID}",  # Google Doc URL
        }

        # Structure the output JSON
        output_json = {
            f"https://docs.google.com/document/d/{DOC_ID}": {
                "text_content": big_string,
                "metadata": metadata,
            },
        }

        # Save the content and metadata to a JSON file
        output_file = "/app/data/processed_google_doc_content.json"
        with open(output_file, "w") as file:
            json.dump(output_json, file, indent=4)
        print(f"Processed content saved to /app/data/processed_google_doc_content.json")
        # saved to dvc folder to upload to gcp
        with open(
            "/app/gcp_dynamic_data/processed_google_doc_content.json", "w"
        ) as json_file:
            json.dump(output_json, json_file, indent=4)
        print(
            f"Processed content saved to /app/gcp_dynamic_data/processed_google_doc_content.json"
        )
    else:
        print("Failed to fetch Google Doc content")


if __name__ == "__main__":
    main()
