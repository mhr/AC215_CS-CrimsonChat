from typing import List, Iterable, Dict
from langchain.schema import Document
from utils.semantic_splitter import SemanticChunker
from utils.simple_text_splitter import SimpleChunker
from typing import List, Iterable, Dict, Callable, Optional

def run_chunking(
    documents: Iterable[Document], 
    config: Dict, 
    embedding_function: Optional[Callable] = None
) -> List[Document]:
    """
    Run chunking on the input documents based on the specified method in the config.

    Args:
        documents (Iterable[Document]): An iterable of LangChain Document objects to be split.
        config (Dict): A dictionary containing configuration parameters.
        embedding_function (Optional[Callable]): A function to generate embeddings for semantic chunking.

    Returns:
        List[Document]: A list of LangChain Document objects representing the chunks.

    Raises:
        ValueError: If semantic chunking is specified without providing an embedding function.
    """
    chunking_method = config.get("chunking_method", "simple")

    if chunking_method == "simple":
        chunker = SimpleChunker(
            chunk_size=config.get("chunk_size", 500),
            chunk_overlap=config.get("chunk_overlap", 20)
        )
    elif chunking_method == "semantic":
        if embedding_function is None:
            raise ValueError("Semantic chunking requires an embedding function. Please provide one.")
        chunker = SemanticChunker(
            embedding_function=embedding_function,
            breakpoint_threshold_type=config.get("breakpoint_threshold_type", "percentile"),
            breakpoint_threshold_amount=config.get("breakpoint_threshold_amount", 95),
            buffer_size=config.get("buffer_size", 1)
        )
    else:
        raise ValueError(f"Invalid chunking method: {chunking_method}")
    return chunker.transform_documents(documents)