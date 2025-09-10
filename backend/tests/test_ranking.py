"""Unit tests for ranking utilities."""

from datetime import UTC, datetime, timedelta

from reddit_pipeline.models import Post
from reddit_pipeline.ranking import composite_rank, rank_posts


class TestCompositeRank:
    """Test composite ranking score calculation."""

    def test_basic_ranking(self):
        """Test basic ranking with score and comments."""
        now = datetime.now(UTC)
        score = composite_rank(score=100, comments=50, upvote_ratio=None, created_utc=now)
        
        # Base score: 1.0 * 100 + 0.5 * 50 = 125
        # No decay for fresh post
        assert score == 125.0

    def test_with_upvote_ratio(self):
        """Test ranking with upvote ratio bonus."""
        now = datetime.now(UTC)
        score = composite_rank(score=100, comments=50, upvote_ratio=0.8, created_utc=now)
        
        # Base: 125, ratio bonus: 2.0 * 0.8 = 1.6
        assert score == 126.6

    def test_time_decay(self):
        """Test that older posts get lower scores."""
        now = datetime.now(UTC)
        fresh = now
        old = now - timedelta(hours=48)  # 48 hours = half-life
        
        fresh_score = composite_rank(100, 50, None, fresh)
        old_score = composite_rank(100, 50, None, old)
        
        # Old post should have ~50% of fresh score due to half-life
        assert old_score < fresh_score
        assert abs(old_score / fresh_score - 0.5) < 0.1

    def test_very_old_post(self):
        """Test very old posts get minimal scores."""
        very_old = datetime.now(UTC) - timedelta(days=30)
        score = composite_rank(1000, 100, 0.9, very_old)
        
        # Should be very small due to exponential decay
        assert score < 1.0

    def test_zero_values(self):
        """Test handling of zero values."""
        now = datetime.now(UTC)
        score = composite_rank(score=0, comments=0, upvote_ratio=0.0, created_utc=now)
        assert score == 0.0

    def test_negative_values(self):
        """Test handling of negative values."""
        now = datetime.now(UTC)
        score = composite_rank(score=-10, comments=-5, upvote_ratio=-0.1, created_utc=now)
        
        # Should handle negative values gracefully
        assert score < 0


class TestRankPosts:
    """Test post ranking and sorting."""

    def test_rank_posts_basic(self):
        """Test basic post ranking."""
        now = datetime.now(UTC)
        posts = [
            Post(
                id="1",
                title="Low score post",
                score=10,
                num_comments=5,
                created_utc=now,
                subreddit="test",
                author="user1",
                url="https://example.com/1",
                text="",
            ),
            Post(
                id="2", 
                title="High score post",
                score=100,
                num_comments=50,
                created_utc=now,
                subreddit="test",
                author="user2",
                url="https://example.com/2",
                text="",
            ),
        ]
        
        ranked = rank_posts(posts)
        
        # Higher scoring post should come first
        assert ranked[0].id == "2"
        assert ranked[1].id == "1"

    def test_rank_posts_same_score_different_comments(self):
        """Test ranking when scores are same but comments differ."""
        now = datetime.now(UTC)
        posts = [
            Post(
                id="1",
                title="Few comments",
                score=100,
                num_comments=10,
                created_utc=now,
                subreddit="test",
                author="user1",
                url="https://example.com/1",
                text="",
            ),
            Post(
                id="2",
                title="Many comments", 
                score=100,
                num_comments=50,
                created_utc=now,
                subreddit="test",
                author="user2",
                url="https://example.com/2",
                text="",
            ),
        ]
        
        ranked = rank_posts(posts)
        
        # Post with more comments should rank higher
        assert ranked[0].id == "2"
        assert ranked[1].id == "1"

    def test_rank_posts_time_decay(self):
        """Test that newer posts rank higher with same engagement."""
        now = datetime.now(UTC)
        fresh = now
        old = now - timedelta(hours=24)
        
        posts = [
            Post(
                id="1",
                title="Old post",
                score=100,
                num_comments=50,
                created_utc=old,
                subreddit="test",
                author="user1",
                url="https://example.com/1",
                text="",
            ),
            Post(
                id="2",
                title="Fresh post",
                score=100,
                num_comments=50,
                created_utc=fresh,
                subreddit="test",
                author="user2",
                url="https://example.com/2",
                text="",
            ),
        ]
        
        ranked = rank_posts(posts)
        
        # Fresh post should rank higher
        assert ranked[0].id == "2"
        assert ranked[1].id == "1"

    def test_rank_posts_empty_list(self):
        """Test ranking empty list."""
        ranked = rank_posts([])
        assert ranked == []

    def test_rank_posts_single_post(self):
        """Test ranking single post."""
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
        
        ranked = rank_posts([post])
        assert len(ranked) == 1
        assert ranked[0].id == "1"
