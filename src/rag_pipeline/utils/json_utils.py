import json
from typing import List
from langchain.schema import Document

    
def load_json_to_documents(file_path: str) -> List[Document]:
    with open(file_path, 'r') as file:
        data = json.load(file)
    documents = []
    for item in data['texts']:
        doc = Document(
            page_content=item['text'],
            metadata={
                'id': item['id'],
                'url': item['url'],
                'timestamp': item['timestamp']
            }
        )
        documents.append(doc)
    return documents