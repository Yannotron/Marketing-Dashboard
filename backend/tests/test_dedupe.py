"""Unit tests for deduplication utilities."""

from datetime import UTC, datetime

from reddit_pipeline.dedupe import dedupe_posts
from reddit_pipeline.models import Post


class TestDedupePosts:
    """Test post deduplication functionality."""

    def test_dedupe_no_duplicates(self):
        """Test deduplication with no duplicates."""
        now = datetime.now(UTC)
        posts = [
            Post(
                id="1",
                title="Post 1",
                score=100,
                num_comments=50,
                created_utc=now,
                subreddit="test",
                author="user1",
                url="https://example.com/1",
                text="",
            ),
            Post(
                id="2",
                title="Post 2",
                score=200,
                num_comments=75,
                created_utc=now,
                subreddit="test",
                author="user2",
                url="https://example.com/2",
                text="",
            ),
        ]
        
        deduped = dedupe_posts(posts)
        
        assert len(deduped) == 2
        assert deduped[0].id == "1"
        assert deduped[1].id == "2"

    def test_dedupe_with_duplicates(self):
        """Test deduplication with duplicate IDs."""
        now = datetime.now(UTC)
        posts = [
            Post(
                id="1",
                title="Post 1",
                score=100,
                num_comments=50,
                created_utc=now,
                subreddit="test",
                author="user1",
                url="https://example.com/1",
                text="",
            ),
            Post(
                id="2",
                title="Post 2",
                score=200,
                num_comments=75,
                created_utc=now,
                subreddit="test",
                author="user2",
                url="https://example.com/2",
                text="",
            ),
            Post(
                id="1",  # Duplicate ID
                title="Post 1 Duplicate",
                score=300,
                num_comments=100,
                created_utc=now,
                subreddit="test",
                author="user3",
                url="https://example.com/3",
                text="",
            ),
        ]
        
        deduped = dedupe_posts(posts)
        
        assert len(deduped) == 2
        # Should keep first occurrence
        assert deduped[0].id == "1"
        assert deduped[0].title == "Post 1"
        assert deduped[0].score == 100
        assert deduped[1].id == "2"

    def test_dedupe_multiple_duplicates(self):
        """Test deduplication with multiple duplicates of same ID."""
        now = datetime.now(UTC)
        posts = [
            Post(
                id="1",
                title="First",
                score=100,
                num_comments=50,
                created_utc=now,
                subreddit="test",
                author="user1",
                url="https://example.com/1",
                text="",
            ),
            Post(
                id="1",  # Duplicate 1
                title="Second",
                score=200,
                num_comments=75,
                created_utc=now,
                subreddit="test",
                author="user2",
                url="https://example.com/2",
                text="",
            ),
            Post(
                id="1",  # Duplicate 2
                title="Third",
                score=300,
                num_comments=100,
                created_utc=now,
                subreddit="test",
                author="user3",
                url="https://example.com/3",
                text="",
            ),
        ]
        
        deduped = dedupe_posts(posts)
        
        assert len(deduped) == 1
        assert deduped[0].id == "1"
        assert deduped[0].title == "First"  # First occurrence kept
        assert deduped[0].score == 100

    def test_dedupe_empty_list(self):
        """Test deduplication of empty list."""
        deduped = dedupe_posts([])
        assert deduped == []

    def test_dedupe_single_post(self):
        """Test deduplication of single post."""
        now = datetime.now(UTC)
        post = Post(
            id="1",
            title="Single post",
            score=100,
            num_comments=50,
            created_utc=now,
            subreddit="test",
            author="user1",
            url="https://example.com/1",
            text="",
        )
        
        deduped = dedupe_posts([post])
        assert len(deduped) == 1
        assert deduped[0].id == "1"

    def test_dedupe_preserves_order(self):
        """Test that deduplication preserves order of first occurrences."""
        now = datetime.now(UTC)
        posts = [
            Post(
                id="3", title="Third", score=300, num_comments=30,
                created_utc=now, subreddit="test", author="user3",
                url="https://example.com/3", text=""
            ),
            Post(
                id="1", title="First", score=100, num_comments=10,
                created_utc=now, subreddit="test", author="user1",
                url="https://example.com/1", text=""
            ),
            Post(
                id="2", title="Second", score=200, num_comments=20,
                created_utc=now, subreddit="test", author="user2",
                url="https://example.com/2", text=""
            ),
            Post(
                id="1", title="First Duplicate", score=150, num_comments=15,
                created_utc=now, subreddit="test", author="user4",
                url="https://example.com/4", text=""
            ),
            Post(
                id="2", title="Second Duplicate", score=250, num_comments=25,
                created_utc=now, subreddit="test", author="user5",
                url="https://example.com/5", text=""
            ),
        ]
        
        deduped = dedupe_posts(posts)
        
        assert len(deduped) == 3
        assert deduped[0].id == "3"
        assert deduped[1].id == "1"
        assert deduped[2].id == "2"
