"""
semantic_splitter.py

Experimental **text splitter** based on semantic similarity.
Ref: https://github.com/dlops-io/llm-rag/blob/main/semantic_splitter.py

This module implements a semantic text splitter that divides documents into
chunks based on semantic similarity using sentence embeddings.

The main class, SemanticChunker, provides functionality to split text or
documents into semantically coherent chunks. It uses cosine distance between
sentence embeddings to determine split points.

How it works:
1. Initial Sentence Splitting:
   The text is first split into individual sentences using a regular expression 
   (by default, splitting on '.', '?', and '!').
2. Sentence Combination:
   Each sentence is combined with its neighboring sentences based on a "buffer size". 
   This creates "combined sentences" that include context from surrounding sentences.
3. Embedding:
   These combined sentences are then embedded. This is where the embedding happens, 
   and it occurs before the final chunking.
4. Distance Calculation:
   The cosine distance is calculated between the embeddings of adjacent combined sentences. 
   This is how the "distance" is measured in this algorithm.
5. Threshold Determination:
   Based on these distances, a threshold is determined using one of the methods 
   we discussed earlier (percentile, standard deviation, etc.).
6. Final Chunking:
   The text is then split into chunks at points where the distance between 
   adjacent combined sentences exceeds this threshold.

Key Features:
- Splits text based on semantic similarity rather than character count
- Configurable splitting threshold using various statistical methods
- Preserves document metadata
- Compatible with LangChain's document processing pipeline

Usage:
    from semantic_splitter import SemanticChunker
    from your_embedding_module import your_embedding_function
    from langchain_core.documents import Document

    chunker = SemanticChunker(embedding_function=your_embedding_function)
    documents = [Document(page_content="Your long text here", metadata={"source": "example.txt"})]
    split_docs = chunker.transform_documents(documents)

Input:
    The 'documents' parameter should be an Iterable of LangChain Document objects.
    Each LangChain Document object should have:
    - page_content: A string containing the text to be split
    - metadata: A dictionary containing any relevant metadata

Output:
    The function returns a List of LangChain Document objects, where each Document
    represents a chunk of the original text, preserving the original metadata.

Dependencies:
- numpy
- langchain_community.utils.math
- langchain_core.documents

Last Modified: 10/10/2024
"""
import copy
import re
from typing import Any, Dict, Iterable, List, Literal, Optional, Sequence, Tuple, cast
import numpy as np
from langchain_community.utils.math import cosine_similarity
from langchain_core.documents import BaseDocumentTransformer, Document
# from langchain_core.embeddings import Embeddings


def combine_sentences(sentences: List[dict], buffer_size: int = 1) -> List[dict]:
    """Combine sentences based on buffer size.

    Args:
        sentences: List of sentences to combine.
        buffer_size: Number of sentences to combine. Defaults to 1.

    Returns:
        List of sentences with combined sentences.
    """

    # Go through each sentence dict
    for i in range(len(sentences)):
        # Create a string that will hold the sentences which are joined
        combined_sentence = ""

        # Add sentences before the current one, based on the buffer size.
        for j in range(i - buffer_size, i):
            # Check if the index j is not negative
            # (to avoid index out of range like on the first one)
            if j >= 0:
                # Add the sentence at index j to the combined_sentence string
                combined_sentence += sentences[j]["sentence"] + " "

        # Add the current sentence
        combined_sentence += sentences[i]["sentence"]

        # Add sentences after the current one, based on the buffer size
        for j in range(i + 1, i + 1 + buffer_size):
            # Check if the index j is within the range of the sentences list
            if j < len(sentences):
                # Add the sentence at index j to the combined_sentence string
                combined_sentence += " " + sentences[j]["sentence"]

        # Then add the whole thing to your dict
        # Store the combined sentence in the current sentence dict
        sentences[i]["combined_sentence"] = combined_sentence

    return sentences


def calculate_cosine_distances(sentences: List[dict]) -> Tuple[List[float], List[dict]]:
    """Calculate cosine distances between sentences.

    Args:
        sentences: List of sentences to calculate distances for.

    Returns:
        Tuple of distances and sentences.
    """
    distances = []
    for i in range(len(sentences) - 1):
        embedding_current = sentences[i]["combined_sentence_embedding"]
        embedding_next = sentences[i + 1]["combined_sentence_embedding"]

        # Calculate cosine similarity
        similarity = cosine_similarity([embedding_current], [embedding_next])[0][0]

        # Convert to cosine distance
        distance = 1 - similarity

        # Append cosine distance to the list
        distances.append(distance)

        # Store distance in the dictionary
        sentences[i]["distance_to_next"] = distance

    # Optionally handle the last sentence
    # sentences[-1]['distance_to_next'] = None  # or a default value

    return distances, sentences


BreakpointThresholdType = Literal[
    "percentile", "standard_deviation", "interquartile", "gradient"
]
BREAKPOINT_DEFAULTS: Dict[BreakpointThresholdType, float] = {
    "percentile": 95,
    "standard_deviation": 3,
    "interquartile": 1.5,
    "gradient": 95,
}


class SemanticChunker(BaseDocumentTransformer):
    """Split the text based on semantic similarity.

    Taken from Greg Kamradt's wonderful notebook:
    https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/tutorials/LevelsOfTextSplitting/5_Levels_Of_Text_Splitting.ipynb

    All credits to him.

    At a high level, this splits into sentences, then groups into groups of 3
    sentences, and then merges one that are similar in the embedding space.
    """

    def __init__(
        self,
        buffer_size: int = 1,
        add_start_index: bool = False,
        breakpoint_threshold_type: BreakpointThresholdType = "percentile",
        breakpoint_threshold_amount: Optional[float] = None,
        number_of_chunks: Optional[int] = None,
        sentence_split_regex: str = r"(?<=[.?!])\s+",
        embedding_function = None,
    ):
        self._add_start_index = add_start_index
        self.buffer_size = buffer_size
        self.breakpoint_threshold_type = breakpoint_threshold_type
        self.number_of_chunks = number_of_chunks
        self.sentence_split_regex = sentence_split_regex
        if breakpoint_threshold_amount is None:
            self.breakpoint_threshold_amount = BREAKPOINT_DEFAULTS[
                breakpoint_threshold_type
            ]
        else:
            self.breakpoint_threshold_amount = breakpoint_threshold_amount
        self.embedding_function = embedding_function

    def _calculate_breakpoint_threshold(
        self, distances: List[float]
    ) -> Tuple[float, List[float]]:
        if self.breakpoint_threshold_type == "percentile":
            return cast(
                float,
                np.percentile(distances, self.breakpoint_threshold_amount),
            ), distances
        elif self.breakpoint_threshold_type == "standard_deviation":
            return cast(
                float,
                np.mean(distances)
                + self.breakpoint_threshold_amount * np.std(distances),
            ), distances
        elif self.breakpoint_threshold_type == "interquartile":
            q1, q3 = np.percentile(distances, [25, 75])
            iqr = q3 - q1

            return np.mean(
                distances
            ) + self.breakpoint_threshold_amount * iqr, distances
        elif self.breakpoint_threshold_type == "gradient":
            # Calculate the threshold based on the distribution of gradient of distance array. # noqa: E501
            distance_gradient = np.gradient(distances, range(0, len(distances)))
            return cast(
                float,
                np.percentile(distance_gradient, self.breakpoint_threshold_amount),
            ), distance_gradient
        else:
            raise ValueError(
                f"Got unexpected `breakpoint_threshold_type`: "
                f"{self.breakpoint_threshold_type}"
            )

    def _threshold_from_clusters(self, distances: List[float]) -> float:
        """
        Calculate the threshold based on the number of chunks.
        Inverse of percentile method.
        """
        if self.number_of_chunks is None:
            raise ValueError(
                "This should never be called if `number_of_chunks` is None."
            )
        x1, y1 = len(distances), 0.0
        x2, y2 = 1.0, 100.0

        x = max(min(self.number_of_chunks, x1), x2)

        # Linear interpolation formula
        if x2 == x1:
            y = y2
        else:
            y = y1 + ((y2 - y1) / (x2 - x1)) * (x - x1)

        y = min(max(y, 0), 100)

        return cast(float, np.percentile(distances, y))
    

    def _calculate_sentence_distances(
        self, single_sentences_list: List[str]
    ) -> Tuple[List[float], List[dict]]:
        """Split text into multiple components."""

        _sentences = [
            {"sentence": x, "index": i} for i, x in enumerate(single_sentences_list)
        ]
        sentences = combine_sentences(_sentences, self.buffer_size)
        #print(sentences)
        # embeddings = self.embeddings.embed_documents(
        #     [x["combined_sentence"] for x in sentences]
        # )
        embeddings = self.embedding_function([x["combined_sentence"] for x in sentences],batch_size=50)
        for i, sentence in enumerate(sentences):
            sentence["combined_sentence_embedding"] = embeddings[i]

        return calculate_cosine_distances(sentences)

    def split_text(
        self,
        text: str,
    ) -> List[str]:
        # Splitting the essay (by default on '.', '?', and '!')
        single_sentences_list = re.split(self.sentence_split_regex, text)

        # having len(single_sentences_list) == 1 would cause the following
        # np.percentile to fail.
        if len(single_sentences_list) == 1:
            return single_sentences_list
        # similarly, the following np.gradient would fail
        if (
            self.breakpoint_threshold_type == "gradient"
            and len(single_sentences_list) == 2
        ):
            return single_sentences_list
        distances, sentences = self._calculate_sentence_distances(single_sentences_list)
        if self.number_of_chunks is not None:
            breakpoint_distance_threshold = self._threshold_from_clusters(distances)
            breakpoint_array = distances
        else:
            (
                breakpoint_distance_threshold,
                breakpoint_array,
            ) = self._calculate_breakpoint_threshold(distances)

        indices_above_thresh = [
            i
            for i, x in enumerate(breakpoint_array)
            if x > breakpoint_distance_threshold
        ]

        chunks = []
        start_index = 0

        # Iterate through the breakpoints to slice the sentences
        for index in indices_above_thresh:
            # The end index is the current breakpoint
            end_index = index

            # Slice the sentence_dicts from the current start index to the end index
            group = sentences[start_index : end_index + 1]
            combined_text = " ".join([d["sentence"] for d in group])
            chunks.append(combined_text)

            # Update the start index for the next group
            start_index = index + 1

        # The last group, if any sentences remain
        if start_index < len(sentences):
            combined_text = " ".join([d["sentence"] for d in sentences[start_index:]])
            chunks.append(combined_text)
        return chunks

    def create_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> List[Document]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = []
        for i, text in enumerate(texts):
            start_index = 0
            for chunk_id, chunk in enumerate(self.split_text(text)):
                metadata = copy.deepcopy(_metadatas[i])
                if self._add_start_index:
                    metadata["start_index"] = start_index
                metadata["chunk_id"] = chunk_id
                new_doc = Document(page_content=chunk, metadata=metadata)
                documents.append(new_doc)
                start_index += len(chunk)
        return documents

    def split_documents(self, documents: Iterable[Document]) -> List[Document]:
        """Split documents."""
        texts, metadatas = [], []
        for doc in documents:
            texts.append(doc.page_content)
            metadatas.append(doc.metadata)
        return self.create_documents(texts, metadatas=metadatas)

    def transform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> Sequence[Document]:
        """Transform sequence of documents by splitting them."""
        return self.split_documents(list(documents))
    

# Example usage
if __name__ == "__main__":
    # Define a simple mock embedding function
    def mock_embedding_function(texts, **kwargs):
        return [np.random.rand(384) for _ in texts]  # 384 is a common embedding size

    chunker = SemanticChunker(
        embedding_function=mock_embedding_function,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=90,
        buffer_size=1
    )
    sample_doc = Document(
        page_content="This is a sample text that will be split into smaller chunks using the SemanticChunker. "
                     "It preserves metadata for each chunk. The semantic chunker uses embeddings to determine "
                     "appropriate split points based on the meaning of the text. This example uses a mock "
                     "embedding function for demonstration purposes.",
        metadata={"source": "example.txt"}
    )
    
    result = chunker.transform_documents([sample_doc])

    print(f"Original document:\n{sample_doc.page_content}")
    print(f"\nMetadata: {sample_doc.metadata}")
    print(f"\nNumber of chunks: {len(result)}")
    for i, chunk in enumerate(result, 1):
        print(f"\nChunk {i}:")
        print(f"Content: {chunk.page_content}")
        print(f"Metadata: {chunk.metadata}")