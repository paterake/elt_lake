"""Tests for elt_doc_rag configuration module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from elt_doc_rag.config import DocumentCollection, RagConfig, load_config


class TestDocumentCollection:
    """Tests for DocumentCollection dataclass."""

    def test_from_dict_minimal(self) -> None:
        """Test creating collection from minimal dict."""
        data = {"name": "test_collection"}
        collection = DocumentCollection.from_dict(data)

        assert collection.name == "test_collection"
        assert collection.display_name == "test_collection"
        assert collection.file_paths == []
        assert collection.chunk_size == 1024
        assert collection.chunk_overlap == 200
        assert collection.use_semantic_chunking is False
        assert collection.enabled is True

    def test_from_dict_full(self) -> None:
        """Test creating collection from full dict."""
        data = {
            "name": "test",
            "display_name": "Test Collection",
            "file_paths": ["/path/to/doc.pdf"],
            "chunk_size": 512,
            "chunk_overlap": 100,
            "use_semantic_chunking": True,
            "metadata": {"domain": "test"},
            "enabled": False,
        }
        collection = DocumentCollection.from_dict(data)

        assert collection.name == "test"
        assert collection.display_name == "Test Collection"
        assert collection.file_paths == ["/path/to/doc.pdf"]
        assert collection.chunk_size == 512
        assert collection.chunk_overlap == 100
        assert collection.use_semantic_chunking is True
        assert collection.metadata == {"domain": "test"}
        assert collection.enabled is False

    def test_to_ingest_config(self) -> None:
        """Test converting to ingest config."""
        collection = DocumentCollection(
            name="test",
            display_name="Test",
            file_paths=["/doc.pdf"],
            metadata={"key": "value"},
        )
        config = collection.to_ingest_config()

        assert config["file_paths"] == ["/doc.pdf"]
        assert config["collection_name"] == "test"
        assert config["metadata"]["collection_name"] == "test"
        assert config["metadata"]["display_name"] == "Test"
        assert config["metadata"]["key"] == "value"


class TestRagConfig:
    """Tests for RagConfig dataclass."""

    def test_from_dict_empty(self) -> None:
        """Test creating config from empty dict."""
        data: dict = {}
        config = RagConfig.from_dict(data)

        assert config.collections == []
        assert config.persist_dir == "./chroma_db"
        assert config.embedding_model == "nomic-embed-text"
        assert config.llm_model == "llama3.2"

    def test_from_dict_with_collections(self) -> None:
        """Test creating config with collections."""
        data = {
            "collections": [
                {"name": "col1"},
                {"name": "col2", "enabled": False},
            ],
            "persist_dir": "/custom/path",
        }
        config = RagConfig.from_dict(data)

        assert len(config.collections) == 2
        assert config.collections[0].name == "col1"
        assert config.collections[0].enabled is True
        assert config.collections[1].name == "col2"
        assert config.collections[1].enabled is False
        assert config.persist_dir == "/custom/path"

    def test_get_collection(self) -> None:
        """Test getting collection by name."""
        config = RagConfig(
            collections=[
                DocumentCollection(name="col1"),
                DocumentCollection(name="col2"),
            ]
        )

        assert config.get_collection("col1") is not None
        assert config.get_collection("col2") is not None
        assert config.get_collection("col3") is None

    def test_get_enabled_collections(self) -> None:
        """Test getting only enabled collections."""
        config = RagConfig(
            collections=[
                DocumentCollection(name="col1", enabled=True),
                DocumentCollection(name="col2", enabled=False),
                DocumentCollection(name="col3", enabled=True),
            ]
        )

        enabled = config.get_enabled_collections()
        assert len(enabled) == 2
        assert enabled[0].name == "col1"
        assert enabled[1].name == "col3"

    def test_from_yaml(self) -> None:
        """Test loading config from YAML file."""
        yaml_content = """
collections:
  - name: test
    chunk_size: 512
persist_dir: /test/path
embedding_model: test-model
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            config = RagConfig.from_yaml(f.name)

            assert len(config.collections) == 1
            assert config.collections[0].name == "test"
            assert config.collections[0].chunk_size == 512
            assert config.persist_dir == "/test/path"
            assert config.embedding_model == "test-model"

            Path(f.name).unlink()

    def test_from_yaml_not_found(self) -> None:
        """Test loading non-existent YAML file."""
        with pytest.raises(FileNotFoundError):
            RagConfig.from_yaml("/nonexistent/path.yaml")

    def test_to_ingest_config(self) -> None:
        """Test converting to ingest config."""
        config = RagConfig(
            collections=[DocumentCollection(name="test", file_paths=["/doc.pdf"])],
            persist_dir="/data",
            embedding_model="embed-model",
        )

        ingest_config = config.to_ingest_config("test")

        assert ingest_config["persist_dir"] == "/data"
        assert ingest_config["embedding_model"] == "embed-model"
        assert ingest_config["file_paths"] == ["/doc.pdf"]

    def test_to_ingest_config_not_found(self) -> None:
        """Test converting with invalid collection name."""
        config = RagConfig()

        with pytest.raises(ValueError, match="Collection not found"):
            config.to_ingest_config("nonexistent")


class TestLoadConfig:
    """Tests for load_config convenience function."""

    def test_load_config(self) -> None:
        """Test loading config via convenience function."""
        yaml_content = """
collections:
  - name: from_file
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            config = load_config(f.name)
            assert len(config.collections) == 1
            assert config.collections[0].name == "from_file"

            Path(f.name).unlink()
