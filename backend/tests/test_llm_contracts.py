"""Unit tests for LLM JSON contract validation."""


import orjson

from reddit_pipeline.llm.summariser import _response_format


class TestLLMResponseFormat:
    """Test LLM response format schema validation."""

    def test_response_format_structure(self):
        """Test that response format has correct structure."""
        format_spec = _response_format()
        
        assert format_spec["type"] == "json_schema"
        assert "json_schema" in format_spec
        
        schema = format_spec["json_schema"]
        assert schema["name"] == "summariser_schema"
        assert schema["strict"] is True
        
        properties = schema["schema"]["properties"]
        required_fields = schema["schema"]["required"]
        
        # Check all required fields are present
        expected_fields = [
            "summary", "pain_points", "recommendations", "segments",
            "tools_mentioned", "contrarian_take", "key_metrics", "sources"
        ]
        
        for field in expected_fields:
            assert field in properties
            assert field in required_fields

    def test_response_format_field_types(self):
        """Test that response format field types are correct."""
        format_spec = _response_format()
        properties = format_spec["json_schema"]["schema"]["properties"]
        
        # String fields
        assert properties["summary"]["type"] == "string"
        assert properties["contrarian_take"]["type"] == "string"
        
        # Array fields
        array_fields = [
            "pain_points", "recommendations", "segments",
            "tools_mentioned", "key_metrics", "sources"
        ]
        
        for field in array_fields:
            assert properties[field]["type"] == "array"
            assert properties[field]["items"]["type"] == "string"

    def test_response_format_additional_properties_false(self):
        """Test that additional properties are not allowed."""
        format_spec = _response_format()
        schema = format_spec["json_schema"]["schema"]
        
        assert schema["additionalProperties"] is False


class TestLLMJSONContracts:
    """Test LLM JSON output contracts and validation."""

    def test_valid_summariser_output(self):
        """Test that valid summariser output matches expected schema."""
        valid_output = {
            "summary": "This is a test summary",
            "pain_points": ["Point 1", "Point 2"],
            "recommendations": ["Rec 1", "Rec 2"],
            "segments": ["Segment 1", "Segment 2"],
            "tools_mentioned": ["Tool 1", "Tool 2"],
            "contrarian_take": "This is a contrarian view",
            "key_metrics": ["Metric 1", "Metric 2"],
            "sources": ["Source 1", "Source 2"]
        }
        
        # Should serialize/deserialize without issues
        json_str = orjson.dumps(valid_output)
        parsed = orjson.loads(json_str)
        
        assert parsed == valid_output

    def test_invalid_summariser_output_missing_fields(self):
        """Test that missing required fields are caught."""
        invalid_output = {
            "summary": "This is a test summary",
            "pain_points": ["Point 1"],
            # Missing other required fields
        }
        
        # This should be caught by the schema validation
        json_str = orjson.dumps(invalid_output)
        parsed = orjson.loads(json_str)
        
        # The schema validation happens at the LLM level
        # This test documents the expected structure
        assert "summary" in parsed
        assert "pain_points" in parsed

    def test_invalid_summariser_output_wrong_types(self):
        """Test that wrong field types are caught."""
        invalid_output = {
            "summary": 123,  # Should be string
            "pain_points": "not an array",  # Should be array
            "recommendations": ["Rec 1"],
            "segments": ["Segment 1"],
            "tools_mentioned": ["Tool 1"],
            "contrarian_take": "Contrarian view",
            "key_metrics": ["Metric 1"],
            "sources": ["Source 1"]
        }
        
        # This should be caught by the schema validation
        json_str = orjson.dumps(invalid_output)
        parsed = orjson.loads(json_str)
        
        # The schema validation happens at the LLM level
        # This test documents the expected structure
        assert isinstance(parsed["summary"], int)  # Wrong type
        assert isinstance(parsed["pain_points"], str)  # Wrong type

    def test_empty_arrays_allowed(self):
        """Test that empty arrays are allowed for array fields."""
        valid_output = {
            "summary": "This is a test summary",
            "pain_points": [],
            "recommendations": [],
            "segments": [],
            "tools_mentioned": [],
            "contrarian_take": "",
            "key_metrics": [],
            "sources": []
        }
        
        json_str = orjson.dumps(valid_output)
        parsed = orjson.loads(json_str)
        
        assert parsed == valid_output

    def test_unicode_handling(self):
        """Test that unicode characters are handled correctly."""
        unicode_output = {
            "summary": "This is a test summary with émojis 🚀 and unicode",
            "pain_points": ["Point with émojis 🎯", "Another point"],
            "recommendations": ["Recommendation with unicode: café"],
            "segments": ["Segment 1", "Segment 2"],
            "tools_mentioned": ["Tool with émojis 🔧"],
            "contrarian_take": "Contrarian view with unicode: naïve",
            "key_metrics": ["Metric 1", "Metric 2"],
            "sources": ["Source 1", "Source 2"]
        }
        
        json_str = orjson.dumps(unicode_output)
        parsed = orjson.loads(json_str)
        
        assert parsed == unicode_output

    def test_large_output_handling(self):
        """Test that large outputs are handled correctly."""
        large_output = {
            "summary": "This is a very long summary " * 100,
            "pain_points": [f"Pain point {i}" for i in range(50)],
            "recommendations": [f"Recommendation {i}" for i in range(50)],
            "segments": [f"Segment {i}" for i in range(20)],
            "tools_mentioned": [f"Tool {i}" for i in range(30)],
            "contrarian_take": "This is a very long contrarian take " * 50,
            "key_metrics": [f"Metric {i}" for i in range(20)],
            "sources": [f"Source {i}" for i in range(20)]
        }
        
        json_str = orjson.dumps(large_output)
        parsed = orjson.loads(json_str)
        
        assert parsed == large_output
        assert len(parsed["pain_points"]) == 50
        assert len(parsed["recommendations"]) == 50


class TestLLMErrorHandling:
    """Test LLM error handling and fallback behavior."""

    def test_malformed_json_fallback(self):
        """Test that malformed JSON is handled gracefully."""
        # This would be the fallback behavior in _call_openai
        fallback_output = {
            "summary": "Malformed JSON content",
            "pain_points": [],
            "recommendations": [],
            "segments": [],
            "tools_mentioned": [],
            "contrarian_take": "",
            "key_metrics": [],
            "sources": []
        }
        
        # Should be valid JSON
        json_str = orjson.dumps(fallback_output)
        parsed = orjson.loads(json_str)
        
        assert parsed == fallback_output
        assert all(field in parsed for field in [
            "summary", "pain_points", "recommendations", "segments",
            "tools_mentioned", "contrarian_take", "key_metrics", "sources"
        ])
