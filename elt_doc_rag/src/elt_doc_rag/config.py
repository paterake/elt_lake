"""Configuration management for document collections."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class DocumentCollection:
    """Configuration for a single document collection.

    Attributes:
        name: Unique collection identifier.
        display_name: Human-readable name.
        file_paths: List of document file paths to ingest.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.
        use_semantic_chunking: Whether to use semantic chunking.
        metadata: Additional metadata to attach to all documents.
        enabled: Whether this collection is enabled.
    """

    name: str
    display_name: str
    file_paths: list[str] = field(default_factory=list)
    chunk_size: int = 1024
    chunk_overlap: int = 200
    use_semantic_chunking: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentCollection":
        """Create a DocumentCollection from a dictionary.

        Args:
            data: Dictionary with collection configuration.

        Returns:
            DocumentCollection instance.
        """
        return cls(
            name=data.get("name", ""),
            display_name=data.get("display_name", data.get("name", "")),
            file_paths=data.get("file_paths", []),
            chunk_size=data.get("chunk_size", 1024),
            chunk_overlap=data.get("chunk_overlap", 200),
            use_semantic_chunking=data.get("use_semantic_chunking", False),
            metadata=data.get("metadata", {}),
            enabled=data.get("enabled", True),
        )

    def to_ingest_config(self) -> dict[str, Any]:
        """Convert to ingestion configuration format.

        Returns:
            Dictionary suitable for passing to elt_llm_rag.ingest.
        """
        return {
            "file_paths": self.file_paths,
            "collection_name": self.name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "metadata": {
                **self.metadata,
                "collection_name": self.name,
                "display_name": self.display_name,
            },
        }


@dataclass
class RagConfig:
    """Root configuration for RAG document collections.

    Attributes:
        collections: List of document collection configurations.
        persist_dir: Base directory for Chroma persistence.
        embedding_model: Ollama embedding model name.
        llm_model: Ollama LLM model name.
        base_url: Ollama server base URL.
        similarity_top_k: Default number of chunks to retrieve.
        system_prompt: Default system prompt for queries.
    """

    collections: list[DocumentCollection] = field(default_factory=list)
    persist_dir: str = "./chroma_db"
    embedding_model: str = "nomic-embed-text"
    llm_model: str = "llama3.2"
    base_url: str = "http://localhost:11434"
    similarity_top_k: int = 5
    system_prompt: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RagConfig":
        """Create a RagConfig from a dictionary.

        Args:
            data: Dictionary with root configuration.

        Returns:
            RagConfig instance.
        """
        collections = [
            DocumentCollection.from_dict(c) for c in data.get("collections", [])
        ]
        return cls(
            collections=collections,
            persist_dir=data.get("persist_dir", "./chroma_db"),
            embedding_model=data.get("embedding_model", "nomic-embed-text"),
            llm_model=data.get("llm_model", "llama3.2"),
            base_url=data.get("base_url", "http://localhost:11434"),
            similarity_top_k=data.get("similarity_top_k", 5),
            system_prompt=data.get("system_prompt"),
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "RagConfig":
        """Load configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file.

        Returns:
            RagConfig instance.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValueError: If config is invalid.
        """
        config_path = Path(path).expanduser()

        if not config_path.exists():
            logger.error("Configuration file not found: %s", config_path)
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        logger.info("Loading configuration from: %s", config_path)

        with open(config_path) as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            logger.error("Configuration must be a YAML dictionary")
            raise ValueError("Configuration must be a YAML dictionary")

        return cls.from_dict(data)

    def get_collection(self, name: str) -> DocumentCollection | None:
        """Get a collection by name.

        Args:
            name: Collection name.

        Returns:
            DocumentCollection if found, None otherwise.
        """
        for collection in self.collections:
            if collection.name == name:
                return collection
        return None

    def get_enabled_collections(self) -> list[DocumentCollection]:
        """Get all enabled collections.

        Returns:
            List of enabled DocumentCollection instances.
        """
        return [c for c in self.collections if c.enabled]

    def to_ingest_config(self, collection_name: str) -> dict[str, Any]:
        """Get ingestion config for a specific collection.

        Args:
            collection_name: Name of the collection.

        Returns:
            Dictionary with full ingestion configuration.

        Raises:
            ValueError: If collection not found.
        """
        collection = self.get_collection(collection_name)
        if not collection:
            raise ValueError(f"Collection not found: {collection_name}")

        config = collection.to_ingest_config()
        config["persist_dir"] = self.persist_dir
        config["embedding_model"] = self.embedding_model
        config["base_url"] = self.base_url

        return config

    def to_query_config(self, collection_name: str) -> dict[str, Any]:
        """Get query config for a specific collection.

        Args:
            collection_name: Name of the collection.

        Returns:
            Dictionary with full query configuration.

        Raises:
            ValueError: If collection not found.
        """
        collection = self.get_collection(collection_name)
        if not collection:
            raise ValueError(f"Collection not found: {collection_name}")

        return {
            "persist_dir": self.persist_dir,
            "collection_name": collection_name,
            "embedding_model": self.embedding_model,
            "llm_model": self.llm_model,
            "base_url": self.base_url,
            "similarity_top_k": self.similarity_top_k,
            "system_prompt": self.system_prompt,
        }


def load_config(path: str | Path) -> RagConfig:
    """Load configuration from a YAML file.

    Convenience function for loading configuration.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        RagConfig instance.
    """
    return RagConfig.from_yaml(path)
