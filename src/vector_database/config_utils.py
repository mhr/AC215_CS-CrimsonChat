import argparse
from typing import Dict, Any  # , Union, List
# import json
"""
# Terminal usage:
# 1. Run the script with the config file:
python your_script.py --config config.txt
# 2. Override a config value from the command line:
python your_script.py --config config.txt --embedding_model textembedding-gecko@002
# 3. Use semantic chunking instead of simple chunking:
python your_script.py --config config.txt --chunking_method semantic --breakpoint_threshold_type cosine --buffer_size 5 --breakpoint_threshold_amount 0.3
# 4. Use all command-line arguments without a config file:
python your_script.py --testing_json /path/to/test.json --embedding_model textembedding-gecko@001 --chunking_method simple --qdrant_collection milestone_2 --chunk_size 1000 --chunk_overlap 200
"""


def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from a text file."""
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="CLI tool for processing JSON data and embedding")
    parser.add_argument("--query", type=str, help="Query input")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--testing_json", type=str, help="Path to JSON file for testing")
    parser.add_argument("--embedding_model", type=str, help="Model name for Vertex AI embedder")
    parser.add_argument("--chunking_method", type=str, choices=["simple", "semantic"], help="Chunking method")
    parser.add_argument("--qdrant_collection", type=str, help="Name of the Qdrant collection")
    parser.add_argument("--vector_dim", type=int, help="Vector dimension")
    parser.add_argument("--bucket_file_path", type=str, help="Path for json file in bucket")
    # Semantic chunking arguments
    parser.add_argument("--breakpoint_threshold_type", type=str, help="Breakpoint threshold type for semantic chunking")
    parser.add_argument("--buffer_size", type=int, help="Buffer size for semantic chunking")
    parser.add_argument("--breakpoint_threshold_amount", type=float, help="Breakpoint threshold amount for semantic chunking")
    # Simple (recursive) chunking arguments
    parser.add_argument("--chunk_size", type=int, help="Chunk size for simple chunking")
    parser.add_argument("--chunk_overlap", type=int, help="Chunk overlap for simple chunking")
    return parser.parse_args()


def get_configuration() -> Dict[str, Any]:
    """Get the final configuration by combining defaults, config file, and command-line arguments."""
    args = parse_arguments()

    # Default values with correct types
    config = {
        'query': None,
        'testing_json': None,
        'embedding_model': 'textembedding-gecko@001',
        'chunking_method': 'simple',
        'qdrant_collection': 'cs-crimsonchat-ms2',
        'breakpoint_threshold_type': None,
        'buffer_size': None,
        'breakpoint_threshold_amount': None,
        'chunk_size': None,
        'chunk_overlap': None,
        'vector_dim': 768,
        'bucket_file_path': None,
    }

    # Helper function to enforce correct data types
    def convert_type(key: str, value: str) -> Any:
        if key in ["vector_dim", "chunk_size", "chunk_overlap", "buffer_size"]:
            return int(value)
        elif key in ["breakpoint_threshold_amount"]:
            return float(value)
        else:
            return value

    # Load config file if specified
    if args.config:
        file_config = load_config(args.config)
        for key, value in file_config.items():
            if key in config:
                config[key] = convert_type(key, value)

    # Update config with arguments
    for arg, value in vars(args).items():
        if value is not None:
            config[arg] = convert_type(arg, str(value))
    return config


def print_config(config):
    print(f"Embedding model: {config['embedding_model']}")
    print(f"Chunking method: {config['chunking_method']}")
    print(f"Qdrant collection: {config['qdrant_collection']}")

    if config['chunking_method'] == "semantic":
        for key in ['breakpoint_threshold_type', 'buffer_size', 'breakpoint_threshold_amount']:
            if config.get(key):
                print(f"{key.replace('_', ' ').title()}: {config[key]}")
    elif config['chunking_method'] == "simple":
        for key in ['chunk_size', 'chunk_overlap']:
            if config.get(key):
                print(f"{key.replace('_', ' ').title()}: {config[key]}")
