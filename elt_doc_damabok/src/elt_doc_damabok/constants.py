"""Constants for elt_doc_damabok module."""

from __future__ import annotations

# Document processing defaults
DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_CHUNKING_STRATEGY = "page"

# RAG configuration defaults
DEFAULT_TOP_K = 5
DEFAULT_MAX_PROMPT_CHARS = 4000

# Model defaults
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_LLM_MODEL = "llama3.1:8b"

# Supported chunking strategies
SUPPORTED_CHUNKING_STRATEGIES = {"page"}

# Ollama configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_TIMEOUT_SECONDS = 120

# Chroma configuration
DEFAULT_COLLECTION_NAME = "damabok"

# Validation limits
MIN_CHUNK_SIZE = 100
MAX_CHUNK_SIZE = 10000
MIN_CHUNK_OVERLAP = 0
MAX_CHUNK_OVERLAP = 1000
MIN_TOP_K = 1
MAX_TOP_K = 100
