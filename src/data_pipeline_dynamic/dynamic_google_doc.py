import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone

# Load environment variable for service account credentials
SERVICE_ACCOUNT_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
DOC_ID = "1qBfsiK-NNe_dMIsShMSiJe5_Qsc2tmYJMSVzbsMw0RI"


def authenticate_gdocs_gdrive_api():
    """
    Authenticates with the Google Docs and Drive APIs using service account credentials.

    Returns:
        tuple: A tuple containing the authenticated Google Docs and Drive service objects.
    """
    try:
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


def fetch_google_doc_content(doc_id, service):
    """
    Fetches the content of a Google Doc.

    Args:
        doc_id (str): The Google Doc ID.
        service: The Google Docs service object.

    Returns:
        tuple: A tuple containing the document title and the extracted text content.
    """
    try:
        document = service.documents().get(documentId=doc_id).execute()
        title = document.get("title")
        content = document.get("body").get("content")

        doc_text = ""
        for element in content:
            if "paragraph" in element:
                for run in element["paragraph"]["elements"]:
                    if "textRun" in run:
                        doc_text += run["textRun"]["content"]
        return title, doc_text
    except Exception as e:
        print(f"Error fetching document: {e}")
        return None, None


def fetch_last_modified_time(doc_id, drive_service):
    """
    Fetches the last modified time of a Google Doc.

    Args:
        doc_id (str): The Google Doc ID.
        drive_service: The Google Drive service object.

    Returns:
        str or None: The ISO 8601 formatted last modified time or None if unavailable.
    """
    try:
        file_metadata = (
            drive_service.files().get(fileId=doc_id, fields="modifiedTime").execute()
        )
        modified_time = file_metadata.get("modifiedTime")
        if modified_time:
            modified_datetime = datetime.fromisoformat(
                modified_time.replace("Z", "+00:00")
            ).astimezone(timezone.utc)
            return modified_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        return None
    except Exception as e:
        print(f"Error fetching last modified time: {e}")
        return None


def save_json_data(file_path, data):
    """
    Saves data to a JSON file.

    Args:
        file_path (str): The path to the file.
        data (dict): The data to save in JSON format.
    """
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Processed content saved to {file_path}")


def create_metadata(last_modified_time, content_text, doc_id):
    """
    Creates metadata for the scraped data.

    Args:
        last_modified_time (str): The last modified date in ISO 8601 format.
        content_text (str): The full content text of the document.
        doc_id (str): The Google Doc ID.

    Returns:
        dict: A dictionary containing metadata.
    """
    return {
        "last_modified": last_modified_time,
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "word_count": len(content_text.split()),
        "url": f"https://docs.google.com/document/d/{doc_id}",
    }


def main():
    """
    Main function to authenticate, fetch, and process Google Doc content and metadata.
    """
    docs_service, drive_service = authenticate_gdocs_gdrive_api()
    if docs_service is None or drive_service is None:
        return

    title, content = fetch_google_doc_content(DOC_ID, docs_service)
    last_modified_time = fetch_last_modified_time(DOC_ID, drive_service)

    if title and content:
        print(f"Title: {title}\nContent:\n{content}")

        big_string = f"Title: {title}\n\nContent:\n{content}"
        metadata = create_metadata(last_modified_time, big_string, DOC_ID)
        output_json = {
            f"https://docs.google.com/document/d/{DOC_ID}": {
                "text_content": big_string,
                "metadata": metadata,
            },
        }

        save_json_data("/app/data/processed_google_doc_content.json", output_json)
        save_json_data(
            "/app/gcp_dynamic_data/processed_google_doc_content.json", output_json
        )
    else:
        print("Failed to fetch Google Doc content")


if __name__ == "__main__":
    main()
