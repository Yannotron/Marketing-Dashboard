"""Unit tests for security utilities and PII stripping."""

from reddit_pipeline.security import (
    sanitize_for_display,
    strip_pii_from_comment,
    strip_pii_from_comments,
    strip_pii_from_post,
    strip_pii_from_text,
    validate_no_pii_remaining,
)


class TestPIIStripping:
    """Test PII stripping functionality."""

    def test_strip_emails(self):
        """Test that email addresses are stripped."""
        text = "Contact me at john.doe@example.com or admin@company.co.uk"
        result = strip_pii_from_text(text)

        assert "[EMAIL_REDACTED]" in result
        assert "john.doe@example.com" not in result
        assert "admin@company.co.uk" not in result

    def test_strip_phone_numbers(self):
        """Test that phone numbers are stripped."""
        text = "Call me at 123-456-7890 or (555) 123-4567 or +1-800-555-0199"
        result = strip_pii_from_text(text)

        assert "[PHONE_REDACTED]" in result
        assert "123-456-7890" not in result
        assert "(555) 123-4567" not in result
        assert "+1-800-555-0199" not in result

    def test_strip_mixed_pii(self):
        """Test stripping mixed PII types."""
        text = "Email: user@example.com, Phone: 555-123-4567, Website: example.com"
        result = strip_pii_from_text(text)

        assert "[EMAIL_REDACTED]" in result
        assert "[PHONE_REDACTED]" in result
        assert "user@example.com" not in result
        assert "555-123-4567" not in result
        assert "example.com" in result  # Website should remain

    def test_strip_no_pii(self):
        """Test text with no PII remains unchanged."""
        text = "This is a normal comment with no personal information."
        result = strip_pii_from_text(text)

        assert result == text

    def test_strip_empty_text(self):
        """Test handling of empty text."""
        assert strip_pii_from_text("") == ""
        assert strip_pii_from_text(None) is None

    def test_strip_unicode_text(self):
        """Test stripping PII from unicode text."""
        text = "Contact: 用户@example.com or 电话: 123-456-7890"
        result = strip_pii_from_text(text)

        assert "[EMAIL_REDACTED]" in result
        assert "[PHONE_REDACTED]" in result
        assert "用户@example.com" not in result
        assert "123-456-7890" not in result

    def test_strip_edge_cases(self):
        """Test edge cases for PII stripping."""
        # Test with special characters
        text = "Email: test+tag@example.com, Phone: +44 20 7946 0958"
        result = strip_pii_from_text(text)

        assert "[EMAIL_REDACTED]" in result
        assert "[PHONE_REDACTED]" in result
        assert "test+tag@example.com" not in result
        assert "+44 20 7946 0958" not in result

    def test_strip_multiple_occurrences(self):
        """Test stripping multiple occurrences of PII."""
        text = "Email: user@example.com, another email: admin@test.com, phone: 555-123-4567"
        result = strip_pii_from_text(text)

        # Should have multiple redacted placeholders
        assert result.count("[EMAIL_REDACTED]") == 2
        assert result.count("[PHONE_REDACTED]") == 1
        assert "user@example.com" not in result
        assert "admin@test.com" not in result
        assert "555-123-4567" not in result


class TestCommentPIIStripping:
    """Test PII stripping from comment dictionaries."""

    def test_strip_comment_pii(self):
        """Test stripping PII from comment body."""
        comment = {
            "id": "comment1",
            "body": "Contact me at user@example.com or call 555-123-4567",
            "score": 10,
            "author": "commenter1",
        }

        result = strip_pii_from_comment(comment)

        assert result["id"] == "comment1"
        assert result["score"] == 10
        assert result["author"] == "commenter1"
        assert "[EMAIL_REDACTED]" in result["body"]
        assert "[PHONE_REDACTED]" in result["body"]
        assert "user@example.com" not in result["body"]
        assert "555-123-4567" not in result["body"]

    def test_strip_comment_no_pii(self):
        """Test comment with no PII remains unchanged."""
        comment = {
            "id": "comment1",
            "body": "This is a normal comment",
            "score": 10,
            "author": "commenter1",
        }

        result = strip_pii_from_comment(comment)

        assert result == comment

    def test_strip_comment_multiple_text_fields(self):
        """Test stripping PII from multiple text fields."""
        comment = {
            "id": "comment1",
            "body": "Email: user@example.com",
            "text": "Phone: 555-123-4567",
            "content": "Another email: admin@test.com",
            "score": 10,
        }

        result = strip_pii_from_comment(comment)

        assert "[EMAIL_REDACTED]" in result["body"]
        assert "[PHONE_REDACTED]" in result["text"]
        assert "[EMAIL_REDACTED]" in result["content"]
        assert "user@example.com" not in result["body"]
        assert "555-123-4567" not in result["text"]
        assert "admin@test.com" not in result["content"]

    def test_strip_comment_non_dict(self):
        """Test handling of non-dict input."""
        assert strip_pii_from_comment("not a dict") == "not a dict"
        assert strip_pii_from_comment(None) is None
        assert strip_pii_from_comment(123) == 123


class TestCommentsPIIStripping:
    """Test PII stripping from lists of comments."""

    def test_strip_comments_pii(self):
        """Test stripping PII from multiple comments."""
        comments = [
            {"id": "comment1", "body": "Email: user1@example.com", "score": 10},
            {"id": "comment2", "body": "Phone: 555-123-4567", "score": 5},
        ]

        result = strip_pii_from_comments(comments)

        assert len(result) == 2
        assert "[EMAIL_REDACTED]" in result[0]["body"]
        assert "[PHONE_REDACTED]" in result[1]["body"]
        assert "user1@example.com" not in result[0]["body"]
        assert "555-123-4567" not in result[1]["body"]

    def test_strip_comments_empty_list(self):
        """Test handling of empty comment list."""
        result = strip_pii_from_comments([])
        assert result == []

    def test_strip_comments_non_list(self):
        """Test handling of non-list input."""
        assert strip_pii_from_comments("not a list") == "not a list"
        assert strip_pii_from_comments(None) is None


class TestPostPIIStripping:
    """Test PII stripping from post dictionaries."""

    def test_strip_post_pii(self):
        """Test stripping PII from post text fields."""
        post = {
            "id": "post1",
            "title": "Contact me at user@example.com",
            "text": "Phone: 555-123-4567",
            "selftext": "Another email: admin@test.com",
            "score": 100,
        }

        result = strip_pii_from_post(post)

        assert result["id"] == "post1"
        assert result["score"] == 100
        assert "[EMAIL_REDACTED]" in result["title"]
        assert "[PHONE_REDACTED]" in result["text"]
        assert "[EMAIL_REDACTED]" in result["selftext"]
        assert "user@example.com" not in result["title"]
        assert "555-123-4567" not in result["text"]
        assert "admin@test.com" not in result["selftext"]

    def test_strip_post_no_pii(self):
        """Test post with no PII remains unchanged."""
        post = {
            "id": "post1",
            "title": "Normal post title",
            "text": "Normal post content",
            "score": 100,
        }

        result = strip_pii_from_post(post)

        assert result == post

    def test_strip_post_non_dict(self):
        """Test handling of non-dict input."""
        assert strip_pii_from_post("not a dict") == "not a dict"
        assert strip_pii_from_post(None) is None


class TestSanitizeForDisplay:
    """Test sanitization for external display."""

    def test_sanitize_string(self):
        """Test sanitizing string input."""
        text = "Contact: user@example.com, Phone: 555-123-4567"
        result = sanitize_for_display(text)

        assert "[EMAIL_REDACTED]" in result
        assert "[PHONE_REDACTED]" in result
        assert "user@example.com" not in result
        assert "555-123-4567" not in result

    def test_sanitize_dict(self):
        """Test sanitizing dict input."""
        data = {"title": "Email: user@example.com", "body": "Phone: 555-123-4567"}

        result = sanitize_for_display(data)

        assert "[EMAIL_REDACTED]" in result["title"]
        assert "[PHONE_REDACTED]" in result["body"]
        assert "user@example.com" not in result["title"]
        assert "555-123-4567" not in result["body"]

    def test_sanitize_list(self):
        """Test sanitizing list input."""
        data = ["Email: user@example.com", {"body": "Phone: 555-123-4567"}]

        result = sanitize_for_display(data)

        assert "[EMAIL_REDACTED]" in result[0]
        assert "[PHONE_REDACTED]" in result[1]["body"]
        assert "user@example.com" not in result[0]
        assert "555-123-4567" not in result[1]["body"]

    def test_sanitize_other_types(self):
        """Test sanitizing other data types."""
        assert sanitize_for_display(123) == 123
        assert sanitize_for_display(None) is None
        assert sanitize_for_display(True) is True


class TestPIIValidation:
    """Test PII validation functionality."""

    def test_validate_no_pii_clean_text(self):
        """Test validation of clean text."""
        text = "This is a normal comment with no personal information."
        assert validate_no_pii_remaining(text) is True

    def test_validate_no_pii_with_emails(self):
        """Test validation detects remaining emails."""
        text = "Contact me at user@example.com"
        assert validate_no_pii_remaining(text) is False

    def test_validate_no_pii_with_phones(self):
        """Test validation detects remaining phone numbers."""
        text = "Call me at 555-123-4567"
        assert validate_no_pii_remaining(text) is False

    def test_validate_no_pii_empty_text(self):
        """Test validation of empty text."""
        assert validate_no_pii_remaining("") is True
        assert validate_no_pii_remaining(None) is True

    def test_validate_no_pii_redacted_text(self):
        """Test validation of properly redacted text."""
        text = "Contact: [EMAIL_REDACTED], Phone: [PHONE_REDACTED]"
        assert validate_no_pii_remaining(text) is True

    def test_validate_no_pii_mixed_redacted(self):
        """Test validation of mixed redacted and clean text."""
        text = "Contact: [EMAIL_REDACTED], Website: example.com, Phone: [PHONE_REDACTED]"
        assert validate_no_pii_remaining(text) is True
