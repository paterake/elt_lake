"""Tests for JSON configuration loading and saving."""

import json
from datetime import date, timedelta
import pytest
from pathlib import Path
from elt_ingest_rest import (
    IngestConfig,
    IngestConfigJson,
    PaginationConfig,
    PaginationType,
    RestApiIngester,
)


class TestJsonConfigLoading:
    """Test loading configuration from JSON."""

    def test_from_json_dict(self):
        """Test creating config from dict."""
        config_dict = {
            "base_url": "https://api.example.com",
            "endpoint": "/data",
            "method": "POST",
            "headers": {"Authorization": "Bearer token123"},
            "params": {"filter": "active"},
            "timeout": 60,
            "pagination": {
                "type": "page_number",
                "page_size": 50,
                "page_param": "page",
                "page_size_param": "limit",
                "data_path": "results",
                "max_pages": 10,
            },
            "output_dir": "./output/test",
            "save_mode": "batch",
            "batch_size": 500,
        }

        config = IngestConfigJson.from_json(config_dict)

        assert config.base_url == "https://api.example.com"
        assert config.endpoint == "/data"
        assert config.method == "POST"
        assert config.headers["Authorization"] == "Bearer token123"
        assert config.params["filter"] == "active"
        assert config.timeout == 60
        assert config.pagination.type == PaginationType.PAGE_NUMBER
        assert config.pagination.page_size == 50
        assert config.pagination.page_param == "page"
        assert config.pagination.page_size_param == "limit"
        assert config.pagination.data_path == "results"
        assert config.pagination.max_pages == 10
        assert "output/test" in str(config.output_dir)
        assert config.save_mode == "batch"
        assert config.batch_size == 500

    def test_from_json_string(self):
        """Test creating config from JSON string."""
        json_str = """
        {
            "base_url": "https://jsonplaceholder.typicode.com",
            "endpoint": "/posts",
            "pagination": {
                "type": "offset_limit",
                "page_size": 10,
                "offset_param": "_start",
                "limit_param": "_limit",
                "data_path": "",
                "max_pages": 2
            },
            "output_dir": "./output/posts"
        }
        """

        config = IngestConfigJson.from_json(json_str)

        assert config.base_url == "https://jsonplaceholder.typicode.com"
        assert config.endpoint == "/posts"
        assert config.pagination.type == PaginationType.OFFSET_LIMIT
        assert config.pagination.offset_param == "_start"
        assert config.pagination.limit_param == "_limit"
        assert config.pagination.max_pages == 2

    def test_from_json_file(self):
        """Test creating config from JSON file."""
        # Use existing example file
        config_file = Path("config/ingest/github_repos.json")

        if not config_file.exists():
            pytest.skip("Example config file not found")

        config = IngestConfigJson.from_json(config_file)

        assert config.base_url == "https://api.github.com"
        assert config.endpoint == "/users/octocat/repos"
        assert config.pagination.type == PaginationType.PAGE_NUMBER
        assert config.headers["Accept"] == "application/vnd.github.v3+json"

    def test_from_json_with_auth(self):
        """Test loading config with authentication."""
        config_dict = {
            "base_url": "https://api.example.com",
            "endpoint": "/protected",
            "auth": ["username", "password"],
            "pagination": {"type": "none"},
        }

        config = IngestConfigJson.from_json(config_dict)

        assert config.auth == ("username", "password")

    def test_from_json_minimal(self):
        """Test loading minimal config (only required fields)."""
        config_dict = {"base_url": "https://api.example.com"}

        config = IngestConfigJson.from_json(config_dict)

        assert config.base_url == "https://api.example.com"
        assert config.endpoint == ""
        assert config.method == "GET"
        assert config.pagination.type == PaginationType.NONE


class TestTemplateResolution:
    def test_date_format_tokens(self):
        assert (
            IngestConfigJson._format_date(date(2026, 3, 10), "dd/mmm/yyyy")
            == "10/Mar/2026"
        )
        assert (
            IngestConfigJson._format_date(date(2026, 3, 10), "yyyy-mm-dd")
            == "2026-03-10"
        )

    def test_from_json_resolves_date_templates(self):
        template = "{date;format=dd/mmm/yyyy;add=-1}"
        expected = IngestConfigJson._format_date(
            date.today() + timedelta(days=-1), "dd/mmm/yyyy"
        )

        config_dict = {
            "base_url": "https://api.example.com",
            "params": {
                "Datefrom": template,
                "Dateto": template,
            },
            "pagination": {"type": "none"},
        }

        config = IngestConfigJson.from_json(config_dict)
        print("template:", template)
        print("expected:", expected)
        print("actual Datefrom:", config.params["Datefrom"])
        print("actual Dateto:", config.params["Dateto"])
        assert config.params["Datefrom"] == expected
        assert config.params["Dateto"] == expected


class TestJsonConfigSaving:
    """Test saving configuration to JSON."""

    def test_to_json_string(self):
        """Test exporting config to JSON string."""
        config = IngestConfig(
            base_url="https://api.example.com",
            endpoint="/data",
            headers={"X-API-Key": "secret123"},
            pagination=PaginationConfig(
                type=PaginationType.PAGE_NUMBER,
                page_size=25,
                data_path="items",
            ),
            output_dir=Path("./output/test"),
        )

        json_str = IngestConfigJson.to_json(
            config,
        )
        data = json.loads(json_str)

        assert data["base_url"] == "https://api.example.com"
        assert data["endpoint"] == "/data"
        assert data["headers"]["X-API-Key"] == "secret123"
        assert data["pagination"]["type"] == "page_number"
        assert data["pagination"]["page_size"] == 25
        assert data["pagination"]["data_path"] == "items"
        assert "output/test" in data["output_dir"]

    def test_to_json_file(self, tmp_path):
        """Test saving config to JSON file."""
        config = IngestConfig(
            base_url="https://pokeapi.co",
            endpoint="/api/v2/pokemon",
            pagination=PaginationConfig(
                type=PaginationType.OFFSET_LIMIT,
                page_size=20,
                offset_param="offset",
                limit_param="limit",
            ),
        )

        output_file = tmp_path / "config.json"
        IngestConfigJson.to_json(config, filepath=output_file)

        # Verify file was created
        assert output_file.exists()

        # Verify content
        with open(output_file, "r") as f:
            data = json.load(f)

        assert data["base_url"] == "https://pokeapi.co"
        assert data["pagination"]["type"] == "offset_limit"
        assert data["pagination"]["offset_param"] == "offset"

    def test_roundtrip_json(self, tmp_path):
        """Test save and load roundtrip."""
        original_config = IngestConfig(
            base_url="https://api.github.com",
            endpoint="/search/repositories",
            params={"q": "language:python"},
            headers={"User-Agent": "Test"},
            pagination=PaginationConfig(
                type=PaginationType.PAGE_NUMBER,
                page_size=10,
                page_param="page",
                page_size_param="per_page",
                data_path="items",
                max_pages=5,
            ),
            output_dir=Path("./output/repos"),
            save_mode="batch",
            batch_size=50,
        )

        # Save to file
        config_file = tmp_path / "roundtrip.json"
        IngestConfigJson.to_json(original_config, filepath=config_file)

        # Load from file
        loaded_config = IngestConfigJson.from_json(config_file)

        # Verify all fields match
        assert loaded_config.base_url == original_config.base_url
        assert loaded_config.endpoint == original_config.endpoint
        assert loaded_config.params == original_config.params
        assert loaded_config.headers == original_config.headers
        assert loaded_config.pagination.type == original_config.pagination.type
        assert (
            loaded_config.pagination.page_size == original_config.pagination.page_size
        )
        assert (
            loaded_config.pagination.data_path == original_config.pagination.data_path
        )
        assert (
            loaded_config.pagination.max_pages == original_config.pagination.max_pages
        )
        assert str(loaded_config.output_dir) == str(original_config.output_dir)
        assert loaded_config.save_mode == original_config.save_mode
        assert loaded_config.batch_size == original_config.batch_size


class TestJsonConfigIntegration:
    """Test using JSON config with actual API requests."""

    def test_load_and_ingest_from_json(self):
        """Test loading config from JSON and running ingestion."""
        config_dict = {
            "base_url": "https://jsonplaceholder.typicode.com",
            "endpoint": "/posts/1",
            "pagination": {"type": "none", "data_path": ""},
            "output_dir": "./output/test/json_config",
        }

        config = IngestConfigJson.from_json(config_dict)
        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 1
        assert data[0]["id"] == 1
        assert "title" in data[0]
        assert output_path.exists()

    def test_load_from_file_and_ingest(self):
        """Test loading from example JSON file and running ingestion."""
        import shutil

        config_file = Path("config/ingest/jsonplaceholder_posts.json")

        if not config_file.exists():
            pytest.skip("Example config file not found")

        # Clean up output directory before test
        output_dir = Path("./output/posts")
        if output_dir.exists():
            shutil.rmtree(output_dir)

        config = IngestConfigJson.from_json(config_file)
        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 30  # 3 pages × 10 records
        assert output_path.is_dir()  # batch mode creates directory

        # Verify batch files were created
        batch_files = list(output_path.glob("*_batch_*.json"))
        assert len(batch_files) == 2  # 30 records / 15 per batch = 2 files


class TestCsvResponseHandling:
    """Test CSV response parsing."""

    def test_ingest_csv_response(self, tmp_path):
        config_dict = {
            "base_url": "https://example.com",
            "endpoint": "/data.csv",
            "headers": {"User-Agent": "Mozilla/5.0"},
            "response_format": "csv",
            "csv_delimiter": ",",
            "csv_skip_rows": 0,
            "pagination": {"type": "none", "data_path": ""},
            "output_dir": str(tmp_path),
            "output_filename": "out.json",
        }

        config = IngestConfigJson.from_json(config_dict)
        ingester = RestApiIngester(config)

        class FakeResponse:
            def __init__(self, text: str):
                self.text = text

            def raise_for_status(self):
                return None

        csv_text = "DATE,XUDLUSS\n01 Jan 2026,1.2345\n"

        def fake_request(*, method, url, params=None, json=None, timeout=None):
            return FakeResponse(csv_text)

        ingester.session.request = fake_request

        data, output_path = ingester.ingest()

        assert data == [{"DATE": "01 Jan 2026", "XUDLUSS": "1.2345"}]
        assert output_path.exists()


class TestXmlResponseHandling:
    """Test XML response parsing."""

    def test_ingest_boe_xml_response(self, tmp_path):
        config_dict = {
            "base_url": "https://example.com",
            "endpoint": "/data.xml",
            "headers": {"User-Agent": "Mozilla/5.0"},
            "response_format": "xml",
            "pagination": {"type": "none", "data_path": ""},
            "output_dir": str(tmp_path),
            "output_filename": "out.json",
        }

        config = IngestConfigJson.from_json(config_dict)
        ingester = RestApiIngester(config)

        class FakeResponse:
            def __init__(self, text: str):
                self.text = text

            def raise_for_status(self):
                return None

        xml_text = """<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns="http://www.gesmes.org/xml/2002-08-01">
  <Cube xmlns="https://www.bankofengland.co.uk/website/agg_series" SCODE="XUDLERS" DESC="Euro into Sterling">
    <Cube TIME="2026-03-02" OBS_VALUE="1.1448" OBS_CONF="N" LAST_UPDATED="2026-03-03 09:30:00"></Cube>
    <Cube TIME="2026-03-03" OBS_VALUE="1.1494" OBS_CONF="N" LAST_UPDATED="2026-03-04 09:30:00"></Cube>
  </Cube>
</Envelope>
"""

        def fake_request(*, method, url, params=None, json=None, timeout=None):
            return FakeResponse(xml_text)

        ingester.session.request = fake_request

        data, output_path = ingester.ingest()

        assert data == [
            {
                "series_code": "XUDLERS",
                "series_description": "Euro into Sterling",
                "time": "2026-03-02",
                "value": "1.1448",
                "obs_conf": "N",
                "last_updated": "2026-03-03 09:30:00",
            },
            {
                "series_code": "XUDLERS",
                "series_description": "Euro into Sterling",
                "time": "2026-03-03",
                "value": "1.1494",
                "obs_conf": "N",
                "last_updated": "2026-03-04 09:30:00",
            },
        ]
        assert output_path.exists()


class TestJsonConfigErrors:
    """Test error handling in JSON configuration."""

    def test_invalid_json_string(self):
        """Test error on invalid JSON string."""
        with pytest.raises(json.JSONDecodeError):
            IngestConfigJson.from_json("{invalid json")

    def test_invalid_pagination_type(self):
        """Test error on invalid pagination type."""
        config_dict = {
            "base_url": "https://api.example.com",
            "pagination": {"type": "invalid_type"},
        }

        with pytest.raises(ValueError):
            IngestConfigJson.from_json(config_dict)

    def test_invalid_input_type(self):
        """Test error on invalid input type."""
        with pytest.raises(TypeError):
            IngestConfigJson.from_json(12345)

    def test_missing_file(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            IngestConfigJson.from_json(Path("nonexistent.json"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
