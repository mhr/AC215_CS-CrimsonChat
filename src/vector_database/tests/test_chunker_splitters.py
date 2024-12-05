import pytest
# from unittest.mock import Mock
from langchain.schema import Document
from ..utils.chunker_utils import run_chunking
from langchain_core.documents import Document
from ..utils.simple_text_splitter import SimpleChunker
from ..utils.semantic_splitter import (
    combine_sentences,
    calculate_cosine_distances,
)

"""
Unit tests for the run_chunking function.

Function Overview:
- Purpose: Splits input documents into chunks based on the specified chunking method and configuration.
- Input:
  - documents: Iterable of LangChain Document objects.
  - config: Dictionary containing configuration parameters.
  - embedding_function: Optional callable for semantic chunking.
- Output:
  - List of LangChain Document objects representing the chunks.
- Errors:
  - Raises ValueError for:
    - Invalid chunking method.
    - Missing embedding_function for semantic chunking.
"""


@pytest.fixture
def sample_documents():
    return [Document(page_content="This is a test document.", metadata={"source": "test.txt"})]


def test_run_chunking_simple_method(sample_documents):
    """
    Test case: Valid input using simple chunking method.
    Input: One document, simple method in config.
    Expected Output: Chunks created by SimpleChunker.
    Why: Verifies basic functionality of the simple chunking method.
    """
    config = {"chunking_method": "simple", "chunk_size": 10, "chunk_overlap": 5}
    output = run_chunking(sample_documents, config)
    assert len(output) > 0
    assert all(isinstance(doc, Document) for doc in output)
    assert all("chunk_id" in doc.metadata for doc in output)


def test_run_chunking_semantic_method_missing_embedding(sample_documents):
    """
    Test case: Semantic chunking without embedding function.
    Input: One document, semantic method in config, no embedding function.
    Expected Output: Raises ValueError.
    Why: Ensures the function handles missing embedding_function for semantic chunking.
    """
    config = {"chunking_method": "semantic"}
    with pytest.raises(ValueError, match="Semantic chunking requires an embedding function"):
        run_chunking(sample_documents, config)


def test_run_chunking_invalid_method(sample_documents):
    """
    Test case: Invalid chunking method.
    Input: One document, invalid method in config.
    Expected Output: Raises ValueError.
    Why: Verifies error handling for unsupported chunking methods.
    """
    config = {"chunking_method": "unsupported"}
    with pytest.raises(ValueError, match="Invalid chunking method: unsupported"):
        run_chunking(sample_documents, config)


"""
Unit tests for the SimpleChunker class.

Class Overview:
- Purpose: Splits input documents into chunks based on character count with specified overlap.
- Input:
  - documents: Iterable of LangChain Document objects.
- Output:
  - List of LangChain Document objects with chunks and updated metadata.
"""


@pytest.fixture
def simple_chunker():
    return SimpleChunker(chunk_size=10, chunk_overlap=5)


@pytest.fixture
def sample_document():
    return Document(
        page_content="This is a sample document to test SimpleChunker functionality.",
        metadata={"source": "example.txt"}
    )


def test_simple_chunker_valid_input(simple_chunker, sample_document):
    """
    Test case: Valid document with standard chunk size and overlap.
    Input: One document.
    Expected Output: List of chunks with correct metadata.
    Why: Verifies basic functionality of the SimpleChunker class.
    """
    result = simple_chunker.transform_documents([sample_document])
    assert len(result) > 0
    assert all(isinstance(doc, Document) for doc in result)
    assert all("chunk_id" in doc.metadata for doc in result)


def test_simple_chunker_empty_input(simple_chunker):
    """
    Test case: Empty input document list.
    Input: []
    Expected Output: []
    Why: Ensures proper handling of no input data.
    """
    result = simple_chunker.transform_documents([])
    assert result == []


def test_simple_chunker_large_chunk_size_with_overlap():
    """
    Test case: Chunk size larger than document length with overlap.
    Input: One document, large chunk size and overlap.
    Expected Output: Single chunk containing the entire document or appropriate overlap behavior.
    Why: Verifies behavior when chunk size exceeds document length, considering overlap.
    """
    # Create a new SimpleChunker instance with large chunk size
    sample_document = Document(
        page_content="This is a document that will test chunking behavior when the chunk size exceeds the document length.",
        metadata={"source": "test_doc.txt"}
    )
    chunk_size = len(sample_document.page_content) + 100  # Ensure chunk size exceeds document length
    simple_chunker = SimpleChunker(chunk_size=chunk_size, chunk_overlap=0)

    # Run chunking
    result = simple_chunker.transform_documents([sample_document])

    # Case 1: Single chunk (chunk size exceeds document length)
    if len(result) == 1:
        assert result[0].page_content == sample_document.page_content
    else:
        # Case 2: Multiple chunks are created due to internal splitter rules
        reconstructed_content = result[0].page_content
        for i in range(1, len(result)):
            previous_chunk = result[i - 1].page_content
            current_chunk = result[i].page_content

            # Dynamically find the overlap
            overlap = ""
            for j in range(1, len(previous_chunk) + 1):
                if current_chunk.startswith(previous_chunk[-j:]):
                    overlap = previous_chunk[-j:]
                    break

            # Concatenate strings based on overlap
            reconstructed_content += current_chunk[len(overlap):]

        # Verify reconstruction matches original document
        assert reconstructed_content == sample_document.page_content, (
            "Reconstructed content does not match original document."
        )


def test_simple_chunker_many_chunks():
    """
    Test case: Chunk size smaller than document length.
    Input: One long document with a small chunk size.
    Expected Output: Multiple chunks created with specified overlap.
    Why: Verifies functionality when a document is split into many chunks.
    """
    # Create a new SimpleChunker instance with the desired parameters
    simple_chunker = SimpleChunker(200, 10)

    # Create a long document
    long_document = Document(
        page_content="This is a very long document meant to be split into multiple chunks for testing purposes. "
                     "It contains a lot of text so that we can verify the chunking behavior and ensure that the "
                     "overlap between chunks works correctly. Each chunk should have the specified size and "
                     "overlap with the previous chunk.",
        metadata={"source": "long_doc.txt"}
    )

    # Run chunking
    result = simple_chunker.transform_documents([long_document])

    # Verify chunks are created
    assert len(result) > 1, "Expected multiple chunks, but only one was created."

    # Reconstruct the content using overlap matching
    reconstructed_content = result[0].page_content
    for i in range(1, len(result)):
        previous_chunk = result[i - 1].page_content
        current_chunk = result[i].page_content

        # Dynamically find the overlap
        overlap = ""
        for j in range(1, len(previous_chunk) + 1):
            if current_chunk.startswith(previous_chunk[-j:]):
                overlap = previous_chunk[-j:]
                break

        # Concatenate strings based on overlap
        reconstructed_content += current_chunk[len(overlap):]

    # Print debug information for validation
    print(f"Chunks: {len(result)}")
    for idx, chunk in enumerate(result):
        print(f"Chunk {idx + 1}: {chunk.page_content}")
    print(f"Reconstructed Content: {reconstructed_content}")

    # Ensure all chunks together match the original content
    assert reconstructed_content == long_document.page_content, (
        "Reconstructed content does not match original document."
    )


"""
Unit tests for functions in semantic_splitter.py.

Function Overview:
- combine_sentences: Combines sentences with a specified buffer size for context.
- calculate_cosine_distances: Calculates cosine distances between embeddings of sentences.
"""


@pytest.fixture
def sample_sentences():
    """
    Sample sentences for testing.
    """
    return [
        {"sentence": "This is the first sentence."},
        {"sentence": "This is the second sentence."},
        {"sentence": "This is the third sentence."},
    ]


@pytest.fixture
def sample_embeddings():
    """
    Sample embeddings for testing cosine distance calculations.
    """
    return [
        {"combined_sentence_embedding": [1, 0, 0]},
        {"combined_sentence_embedding": [0.5, 0.5, 0]},
        {"combined_sentence_embedding": [0, 1, 0]},
    ]


# Test for combine_sentences
def test_combine_sentences_no_buffer(sample_sentences):
    """
    Test case: Combine sentences with a buffer size of 0.
    Input: Sentences with no additional buffer.
    Expected Output: Each sentence remains unchanged.
    Why: Verifies basic behavior when buffer size is zero.
    """
    combined = combine_sentences(sample_sentences, buffer_size=0)
    assert len(combined) == len(sample_sentences)
    for i, sentence in enumerate(sample_sentences):
        assert combined[i]["combined_sentence"] == sentence["sentence"]


def test_combine_sentences_with_buffer(sample_sentences):
    """
    Test case: Combine sentences with a buffer size of 1.
    Input: Sentences with adjacent context.
    Expected Output: Each sentence includes one sentence before and after (where applicable).
    Why: Ensures correct combination of sentences with context.
    """
    combined = combine_sentences(sample_sentences, buffer_size=1)
    assert len(combined) == len(sample_sentences)
    assert combined[0]["combined_sentence"] == (
        "This is the first sentence. This is the second sentence."
    )
    assert combined[1]["combined_sentence"] == (
        "This is the first sentence. This is the second sentence. This is the third sentence."
    )
    assert combined[2]["combined_sentence"] == (
        "This is the second sentence. This is the third sentence."
    )


def test_combine_sentences_large_buffer(sample_sentences):
    """
    Test case: Combine sentences with a buffer size larger than the number of sentences.
    Input: Sentences with buffer size exceeding list length.
    Expected Output: Each combined sentence includes all sentences.
    Why: Verifies handling of large buffer sizes.
    """
    combined = combine_sentences(sample_sentences, buffer_size=10)
    for sentence in combined:
        assert sentence["combined_sentence"] == (
            "This is the first sentence. This is the second sentence. This is the third sentence."
        )


def test_calculate_cosine_distances_empty():
    """
    Test case: Empty sentence list.
    Input: []
    Expected Output: Empty distances and sentences.
    Why: Verifies handling of edge case with no input data.
    """
    distances, sentences = calculate_cosine_distances([])
    assert distances == []
    assert sentences == []


def test_calculate_cosine_distances_single_sentence():
    """
    Test case: Single sentence with no pair for comparison.
    Input: One sentence with embedding.
    Expected Output: No distances calculated.
    Why: Ensures correct handling of single input.
    """
    distances, sentences = calculate_cosine_distances([{"combined_sentence_embedding": [1, 0, 0]}])
    assert distances == []
    assert len(sentences) == 1
    assert "distance_to_next" not in sentences[0]


# Placeholder for the SemanticChunker class tests
@pytest.mark.skip(reason="SemanticChunker requires external embedding function.")
def test_semantic_chunker_class():
    """
    Placeholder for testing SemanticChunker class methods.
    """
    pass
