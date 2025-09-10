"""Unit tests for utility functions."""

import json
import time
from unittest.mock import patch

import pytest

from reddit_pipeline.utils import get_json_logger, retry_with_backoff


class TestJsonLogger:
    """Test JSON logging functionality."""

    def test_get_json_logger_returns_logger(self):
        """Test that get_json_logger returns a logger instance."""
        logger = get_json_logger("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"

    def test_get_json_logger_same_name_returns_same_instance(self):
        """Test that same logger name returns same instance."""
        logger1 = get_json_logger("test_logger")
        logger2 = get_json_logger("test_logger")
        assert logger1 is logger2

    def test_get_json_logger_different_names_return_different_instances(self):
        """Test that different logger names return different instances."""
        logger1 = get_json_logger("test_logger_1")
        logger2 = get_json_logger("test_logger_2")
        assert logger1 is not logger2

    def test_json_logger_format(self):
        """Test that JSON logger formats messages correctly."""
        logger = get_json_logger("test_logger")
        
        # Capture log output
        with patch('sys.stdout') as mock_stdout:
            logger.info("Test message")
            
            # Get the logged message
            call_args = mock_stdout.write.call_args[0][0]
            log_data = json.loads(call_args)
            
            assert log_data["level"] == "INFO"
            assert log_data["name"] == "test_logger"
            assert log_data["message"] == "Test message"
            assert "time" in log_data
            assert isinstance(log_data["time"], int)

    def test_json_logger_with_exception(self):
        """Test that JSON logger handles exceptions correctly."""
        logger = get_json_logger("test_logger")
        
        with patch('sys.stdout') as mock_stdout:
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.exception("Test message with exception")
            
            call_args = mock_stdout.write.call_args[0][0]
            log_data = json.loads(call_args)
            
            assert log_data["level"] == "ERROR"
            assert log_data["message"] == "Test message with exception"
            assert "exc_info" in log_data
            assert "ValueError: Test exception" in log_data["exc_info"]


class TestRetryWithBackoff:
    """Test retry with backoff functionality."""

    def test_retry_success_on_first_attempt(self):
        """Test that function succeeds on first attempt without retry."""
        @retry_with_backoff()
        def success_func():
            return "success"
        
        result = success_func()
        assert result == "success"

    def test_retry_success_after_failures(self):
        """Test that function succeeds after some failures."""
        call_count = 0
        
        @retry_with_backoff(max_attempts=3, base_delay_seconds=0.01)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = flaky_func()
        assert result == "success"
        assert call_count == 3

    def test_retry_exhausts_max_attempts(self):
        """Test that retry raises exception after max attempts."""
        call_count = 0
        
        @retry_with_backoff(max_attempts=2, base_delay_seconds=0.01)
        def always_fail_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            always_fail_func()
        
        assert call_count == 2

    def test_retry_with_specific_exceptions(self):
        """Test that retry only retries on specified exceptions."""
        call_count = 0
        
        @retry_with_backoff(exceptions=(ValueError,), max_attempts=3, base_delay_seconds=0.01)
        def func_with_wrong_exception():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Wrong exception type")
        
        with pytest.raises(RuntimeError, match="Wrong exception type"):
            func_with_wrong_exception()
        
        assert call_count == 1  # Should not retry

    def test_retry_with_correct_exceptions(self):
        """Test that retry works with correct exception types."""
        call_count = 0
        
        @retry_with_backoff(exceptions=(ValueError, RuntimeError), max_attempts=3, base_delay_seconds=0.01)
        def func_with_correct_exception():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "success"
        
        result = func_with_correct_exception()
        assert result == "success"
        assert call_count == 2

    def test_retry_delay_calculation(self):
        """Test that retry delay is calculated correctly."""
        call_count = 0
        delays = []
        
        @retry_with_backoff(max_attempts=3, base_delay_seconds=0.1, max_delay_seconds=0.5)
        def func_with_delay():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                delays.append(time.time())
                raise ValueError("Temporary failure")
            return "success"
        
        start_time = time.time()
        result = func_with_delay()
        
        assert result == "success"
        assert call_count == 3
        assert len(delays) == 2
        
        # Check that delays are increasing (exponential backoff)
        if len(delays) >= 2:
            delay1 = delays[0] - start_time
            delay2 = delays[1] - delays[0]
            assert delay2 > delay1

    def test_retry_preserves_function_metadata(self):
        """Test that retry decorator preserves function metadata."""
        @retry_with_backoff()
        def test_func(arg1, arg2=None):
            """Test function docstring."""
            return f"{arg1}_{arg2}"
        
        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function docstring."

    def test_retry_with_kwargs(self):
        """Test that retry works with keyword arguments."""
        call_count = 0
        
        @retry_with_backoff(max_attempts=3, base_delay_seconds=0.01)
        def func_with_kwargs(a, b, c=None):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return f"{a}_{b}_{c}"
        
        result = func_with_kwargs(1, 2, c=3)
        assert result == "1_2_3"
        assert call_count == 2

    def test_retry_with_args_and_kwargs(self):
        """Test that retry works with both args and kwargs."""
        call_count = 0
        
        @retry_with_backoff(max_attempts=3, base_delay_seconds=0.01)
        def func_with_args_kwargs(a, b, c=None, d=None):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return f"{a}_{b}_{c}_{d}"
        
        result = func_with_args_kwargs(1, 2, c=3, d=4)
        assert result == "1_2_3_4"
        assert call_count == 2