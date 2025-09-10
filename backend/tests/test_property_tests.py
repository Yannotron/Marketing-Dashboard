"""Property tests for idempotent operations and data consistency."""

from datetime import UTC, datetime

import pytest

from reddit_pipeline.dedupe import dedupe_posts
from reddit_pipeline.models import Post
from reddit_pipeline.ranking import rank_posts


class TestIdempotentOperations:
    """Test that operations are idempotent (running twice produces same result)."""

    def test_dedupe_idempotent(self):
        """Test that deduplication is idempotent."""
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
                id="1",  # Duplicate
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
        
        # First deduplication
        deduped_once = dedupe_posts(posts)
        
        # Second deduplication (should be same)
        deduped_twice = dedupe_posts(deduped_once)
        
        # Results should be identical
        assert len(deduped_once) == len(deduped_twice)
        assert deduped_once == deduped_twice

    def test_ranking_idempotent(self):
        """Test that ranking is idempotent."""
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
        
        # First ranking
        ranked_once = rank_posts(posts)
        
        # Second ranking (should be same)
        ranked_twice = rank_posts(ranked_once)
        
        # Results should be identical
        assert len(ranked_once) == len(ranked_twice)
        assert ranked_once == ranked_twice

    def test_dedupe_then_rank_idempotent(self):
        """Test that dedupe then rank is idempotent."""
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
                id="1",  # Duplicate
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
        
        # First dedupe then rank
        result_once = rank_posts(dedupe_posts(posts))
        
        # Second dedupe then rank (should be same)
        result_twice = rank_posts(dedupe_posts(result_once))
        
        # Results should be identical
        assert len(result_once) == len(result_twice)
        assert result_once == result_twice


class TestDataConsistency:
    """Test data consistency properties."""

    def test_dedupe_preserves_post_integrity(self):
        """Test that deduplication preserves post data integrity."""
        now = datetime.now(UTC)
        original_post = Post(
            id="1",
            title="Original Post",
            score=100,
            num_comments=50,
            created_utc=now,
            subreddit="test",
            author="user1",
            url="https://example.com/1",
            text="Original text",
        )
        
        duplicate_post = Post(
            id="1",  # Same ID
            title="Duplicate Post",
            score=200,
            num_comments=75,
            created_utc=now,
            subreddit="test",
            author="user2",
            url="https://example.com/2",
            text="Duplicate text",
        )
        
        posts = [original_post, duplicate_post]
        deduped = dedupe_posts(posts)
        
        # Should keep first occurrence
        assert len(deduped) == 1
        assert deduped[0] == original_post
        assert deduped[0].title == "Original Post"
        assert deduped[0].score == 100

    def test_ranking_preserves_post_integrity(self):
        """Test that ranking preserves post data integrity."""
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
                text="Text 1",
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
                text="Text 2",
            ),
        ]
        
        ranked = rank_posts(posts)
        
        # All posts should be preserved
        assert len(ranked) == 2
        
        # Find posts by ID to verify integrity
        post_1 = next(p for p in ranked if p.id == "1")
        post_2 = next(p for p in ranked if p.id == "2")
        
        assert post_1.title == "Post 1"
        assert post_1.score == 100
        assert post_1.text == "Text 1"
        
        assert post_2.title == "Post 2"
        assert post_2.score == 200
        assert post_2.text == "Text 2"

    def test_empty_input_handling(self):
        """Test that empty inputs are handled consistently."""
        # Empty list
        assert dedupe_posts([]) == []
        assert rank_posts([]) == []
        
        # None input (should raise TypeError)
        with pytest.raises(TypeError):
            dedupe_posts(None)
        
        with pytest.raises(TypeError):
            rank_posts(None)

    def test_single_post_handling(self):
        """Test that single posts are handled consistently."""
        now = datetime.now(UTC)
        post = Post(
            id="1",
            title="Single Post",
            score=100,
            num_comments=50,
            created_utc=now,
            subreddit="test",
            author="user1",
            url="https://example.com/1",
            text="Single text",
        )
        
        # Deduplication should return same post
        deduped = dedupe_posts([post])
        assert len(deduped) == 1
        assert deduped[0] == post
        
        # Ranking should return same post
        ranked = rank_posts([post])
        assert len(ranked) == 1
        assert ranked[0] == post


class TestCommutativeOperations:
    """Test that operations are commutative where expected."""

    def test_dedupe_commutative(self):
        """Test that deduplication order doesn't matter for final result."""
        now = datetime.now(UTC)
        posts_a = [
            Post(id="1", title="A1", score=100, num_comments=50, created_utc=now, subreddit="test", author="user1", url="https://example.com/1", text=""),
            Post(id="2", title="A2", score=200, num_comments=75, created_utc=now, subreddit="test", author="user2", url="https://example.com/2", text=""),
        ]
        
        posts_b = [
            Post(id="2", title="B2", score=300, num_comments=100, created_utc=now, subreddit="test", author="user3", url="https://example.com/3", text=""),
            Post(id="1", title="B1", score=400, num_comments=125, created_utc=now, subreddit="test", author="user4", url="https://example.com/4", text=""),
        ]
        
        # Dedupe A then B
        result_ab = dedupe_posts(posts_a + posts_b)
        
        # Dedupe B then A
        result_ba = dedupe_posts(posts_b + posts_a)
        
        # Results should be identical (same unique IDs)
        assert len(result_ab) == len(result_ba)
        assert set(p.id for p in result_ab) == set(p.id for p in result_ba)

    def test_ranking_commutative(self):
        """Test that ranking order doesn't matter for final result."""
        now = datetime.now(UTC)
        posts_a = [
            Post(id="1", title="A1", score=100, num_comments=50, created_utc=now, subreddit="test", author="user1", url="https://example.com/1", text=""),
            Post(id="2", title="A2", score=200, num_comments=75, created_utc=now, subreddit="test", author="user2", url="https://example.com/2", text=""),
        ]
        
        posts_b = [
            Post(id="3", title="B3", score=300, num_comments=100, created_utc=now, subreddit="test", author="user3", url="https://example.com/3", text=""),
            Post(id="4", title="B4", score=400, num_comments=125, created_utc=now, subreddit="test", author="user4", url="https://example.com/4", text=""),
        ]
        
        # Rank A then B
        result_ab = rank_posts(posts_a + posts_b)
        
        # Rank B then A
        result_ba = rank_posts(posts_b + posts_a)
        
        # Results should be identical (same posts, same order)
        assert len(result_ab) == len(result_ba)
        assert result_ab == result_ba
