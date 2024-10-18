"""
simple_text_splitter.py

A text splitter based on recursive character splitting.
This module implements a simple text splitter that divides documents into
chunks based on character count, with the ability to split recursively.

The main class, SimpleChunker, provides functionality to split text or
documents into chunks of a specified size. It uses the RecursiveCharacterTextSplitter
from LangChain to perform the splitting.

Input Schema (LangChain Document):
    - page_content: str
        The text content to be split.
    - metadata: Dict
        A dictionary containing any relevant metadata for the document.

Output Schema (List of LangChain Documents):
    - page_content: str
        The content of each chunk after splitting.
    - metadata: Dict
        A dictionary containing:
        - Original metadata from the input document
        - chunk_id: int
            A unique identifier for each chunk within a document

Key Features:
- Splits text based on character count with specified overlap
- Preserves document metadata
- Compatible with LangChain's document processing pipeline
- Adds chunk ID to each output chunk's metadata

Usage:
    from simple_text_splitter import SimpleChunker
    from langchain_core.documents import Document

    chunker = SimpleChunker(chunk_size=1000, chunk_overlap=200)
    documents = [Document(page_content="Your long text here", metadata={"source": "example.txt"})]
    split_docs = chunker.transform_documents(documents)

Dependencies:
- langchain.text_splitter
- langchain_core.documents

Last Modified: 10/10/2024
"""

from typing import List, Iterable
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class SimpleChunker:
    def __init__(self, chunk_size: int = 50, chunk_overlap: int = 10):
        """
        Initialize the SimpleChunker.

        Args:
            chunk_size (int): The maximum size of each chunk.
            chunk_overlap (int): The number of characters to overlap between chunks.
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(chunk_size),          # Force chunk_size to be an integer
            chunk_overlap=int(chunk_overlap),    # Force chunk_overlap to be an integer
            length_function=len,  
        )

    def transform_documents(self, documents: Iterable[Document]) -> List[Document]:
        """
        Split the input documents into chunks.

        Args:
            documents (Iterable[Document]): An iterable of LangChain Document objects to be split.

        Returns:
            List[Document]: A list of LangChain Document objects representing the chunks.
        """
        split_docs = []
        for doc in documents:
            splits = self.text_splitter.split_text(doc.page_content)
            for chunk_id, split in enumerate(splits):
                metadata = doc.metadata.copy()
                metadata['chunk_id'] = chunk_id
                split_docs.append(Document(page_content=split, metadata=metadata))
        return split_docs

# Example usage
if __name__ == "__main__":
    chunker = SimpleChunker(chunk_size=50, chunk_overlap=10)
    sample_doc = Document(page_content="This is a sample text that will be split into smaller chunks using the SimpleChunker. It preserves metadata for each chunk.", metadata={"source": "example.txt"})
    
    result = chunker.transform_documents([sample_doc])

    print(f"Original document:\n{sample_doc.page_content}")
    print(f"\nMetadata: {sample_doc.metadata}")
    print(f"\nNumber of chunks: {len(result)}")
    for i, chunk in enumerate(result, 1):
        print(f"\nChunk {i}:")
        print(f"Content: {chunk.page_content}")
        print(f"Metadata: {chunk.metadata}")