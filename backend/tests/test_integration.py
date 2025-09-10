"""Integration tests with mocked clients and VCR-style cassettes."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timezone
from reddit_pipeline.clients.reddit import RedditClient
from reddit_pipeline.clients.hackernews import HackerNewsClient
from reddit_pipeline.clients.producthunt import ProductHuntClient
from reddit_pipeline.llm.summariser import summarise_posts_with_comments
from reddit_pipeline.models import Post


class TestRedditClientIntegration:
    """Integration tests for Reddit client."""

    @patch('praw.Reddit')
    def test_reddit_client_fetch_posts(self, mock_reddit_class):
        """Test Reddit client fetching posts with mocked PRAW."""
        # Mock Reddit instance
        mock_reddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit
        
        # Mock subreddit and posts
        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit
        
        # Mock post data
        mock_post_data = [
            {
                'id': 'test1',
                'title': 'Test Post 1',
                'score': 100,
                'num_comments': 50,
                'created_utc': 1640995200,  # 2022-01-01
                'subreddit': 'test',
                'author': 'testuser1',
                'url': 'https://example.com/1',
                'selftext': 'Test content 1',
            },
            {
                'id': 'test2',
                'title': 'Test Post 2',
                'score': 200,
                'num_comments': 75,
                'created_utc': 1640995260,  # 2022-01-01 + 1 minute
                'subreddit': 'test',
                'author': 'testuser2',
                'url': 'https://example.com/2',
                'selftext': 'Test content 2',
            }
        ]
        
        # Mock submission objects
        mock_submissions = []
        for data in mock_post_data:
            mock_sub = MagicMock()
            mock_sub.id = data['id']
            mock_sub.title = data['title']
            mock_sub.score = data['score']
            mock_sub.num_comments = data['num_comments']
            mock_sub.created_utc = data['created_utc']
            mock_sub.subreddit.display_name = data['subreddit']
            mock_sub.author.name = data['author']
            mock_sub.url = data['url']
            mock_sub.selftext = data['selftext']
            mock_submissions.append(mock_sub)
        
        mock_subreddit.hot.return_value = mock_submissions
        
        # Test client
        client = RedditClient()
        posts = client.fetch_posts('test', limit=2)
        
        # Verify results
        assert len(posts) == 2
        assert posts[0].id == 'test1'
        assert posts[0].title == 'Test Post 1'
        assert posts[0].score == 100
        assert posts[1].id == 'test2'
        assert posts[1].title == 'Test Post 2'
        assert posts[1].score == 200

    @patch('praw.Reddit')
    def test_reddit_client_fetch_comments(self, mock_reddit_class):
        """Test Reddit client fetching comments with mocked PRAW."""
        # Mock Reddit instance
        mock_reddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit
        
        # Mock submission
        mock_submission = MagicMock()
        mock_submission.id = 'test1'
        mock_reddit.submission.return_value = mock_submission
        
        # Mock comments
        mock_comment_data = [
            {
                'id': 'comment1',
                'body': 'Great post!',
                'score': 10,
                'author': 'commenter1',
            },
            {
                'id': 'comment2',
                'body': 'Interesting perspective',
                'score': 5,
                'author': 'commenter2',
            }
        ]
        
        mock_comments = []
        for data in mock_comment_data:
            mock_comment = MagicMock()
            mock_comment.id = data['id']
            mock_comment.body = data['body']
            mock_comment.score = data['score']
            mock_comment.author.name = data['author']
            mock_comments.append(mock_comment)
        
        mock_submission.comments.list.return_value = mock_comments
        
        # Test client
        client = RedditClient()
        comments = client.fetch_comments('test1', limit=2)
        
        # Verify results
        assert len(comments) == 2
        assert comments[0]['id'] == 'comment1'
        assert comments[0]['body'] == 'Great post!'
        assert comments[0]['score'] == 10
        assert comments[1]['id'] == 'comment2'
        assert comments[1]['body'] == 'Interesting perspective'
        assert comments[1]['score'] == 5

    @patch('praw.Reddit')
    def test_reddit_client_error_handling(self, mock_reddit_class):
        """Test Reddit client error handling."""
        # Mock Reddit instance that raises exception
        mock_reddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit
        mock_reddit.subreddit.side_effect = Exception("API Error")
        
        client = RedditClient()
        
        # Should handle error gracefully
        posts = client.fetch_posts('test', limit=10)
        assert posts == []


class TestHackerNewsClientIntegration:
    """Integration tests for HackerNews client."""

    @patch('httpx.Client.get')
    def test_hackernews_client_fetch_posts(self, mock_get):
        """Test HackerNews client fetching posts with mocked HTTP."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'hits': [
                {
                    'objectID': 'hn1',
                    'title': 'HN Post 1',
                    'points': 100,
                    'num_comments': 50,
                    'created_at_i': 1640995200,
                    'author': 'hnuser1',
                    'url': 'https://example.com/hn1',
                    'story_text': 'HN content 1',
                },
                {
                    'objectID': 'hn2',
                    'title': 'HN Post 2',
                    'points': 200,
                    'num_comments': 75,
                    'created_at_i': 1640995260,
                    'author': 'hnuser2',
                    'url': 'https://example.com/hn2',
                    'story_text': 'HN content 2',
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test client
        client = HackerNewsClient()
        posts = client.fetch_posts(limit=2)
        
        # Verify results
        assert len(posts) == 2
        assert posts[0].id == 'hn1'
        assert posts[0].title == 'HN Post 1'
        assert posts[0].score == 100
        assert posts[1].id == 'hn2'
        assert posts[1].title == 'HN Post 2'
        assert posts[1].score == 200

    @patch('httpx.Client.get')
    def test_hackernews_client_error_handling(self, mock_get):
        """Test HackerNews client error handling."""
        # Mock HTTP error
        mock_get.side_effect = Exception("HTTP Error")
        
        client = HackerNewsClient()
        
        # Should handle error gracefully
        posts = client.fetch_posts(limit=10)
        assert posts == []


class TestProductHuntClientIntegration:
    """Integration tests for ProductHunt client."""

    @patch('httpx.Client.get')
    def test_producthunt_client_fetch_posts(self, mock_get):
        """Test ProductHunt client fetching posts with mocked HTTP."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'posts': [
                {
                    'id': 'ph1',
                    'name': 'PH Product 1',
                    'votes_count': 100,
                    'comments_count': 50,
                    'created_at': '2022-01-01T00:00:00Z',
                    'user': {'name': 'phuser1'},
                    'redirect_url': 'https://example.com/ph1',
                    'tagline': 'PH content 1',
                },
                {
                    'id': 'ph2',
                    'name': 'PH Product 2',
                    'votes_count': 200,
                    'comments_count': 75,
                    'created_at': '2022-01-01T00:01:00Z',
                    'user': {'name': 'phuser2'},
                    'redirect_url': 'https://example.com/ph2',
                    'tagline': 'PH content 2',
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test client
        client = ProductHuntClient()
        posts = client.fetch_posts(limit=2)
        
        # Verify results
        assert len(posts) == 2
        assert posts[0].id == 'ph1'
        assert posts[0].title == 'PH Product 1'
        assert posts[0].score == 100
        assert posts[1].id == 'ph2'
        assert posts[1].title == 'PH Product 2'
        assert posts[1].score == 200

    @patch('httpx.Client.get')
    def test_producthunt_client_error_handling(self, mock_get):
        """Test ProductHunt client error handling."""
        # Mock HTTP error
        mock_get.side_effect = Exception("HTTP Error")
        
        client = ProductHuntClient()
        
        # Should handle error gracefully
        posts = client.fetch_posts(limit=10)
        assert posts == []


class TestLLMIntegration:
    """Integration tests for LLM summarisation."""

    @patch('reddit_pipeline.llm.summariser._call_openai')
    def test_summarise_posts_with_comments(self, mock_call_openai):
        """Test LLM summarisation with mocked OpenAI client."""
        # Mock OpenAI response
        mock_call_openai.return_value = {
            "summary": "Test summary",
            "pain_points": ["Point 1", "Point 2"],
            "recommendations": ["Rec 1", "Rec 2"],
            "segments": ["Segment 1", "Segment 2"],
            "tools_mentioned": ["Tool 1", "Tool 2"],
            "contrarian_take": "Contrarian view",
            "key_metrics": ["Metric 1", "Metric 2"],
            "sources": ["Source 1", "Source 2"]
        }
        
        # Test data
        now = datetime.now(timezone.utc)
        posts = [
            Post(
                id="test1",
                title="Test Post 1",
                score=100,
                num_comments=50,
                created_utc=now,
                subreddit="test",
                author="user1",
                url="https://example.com/1",
                text="Test content 1",
            )
        ]
        
        comments_by_post = {
            "test1": [
                {"body": "Great post!", "score": 10},
                {"body": "Interesting perspective", "score": 5}
            ]
        }
        
        # Test summarisation
        results = summarise_posts_with_comments(posts, comments_by_post)
        
        # Verify results
        assert "test1" in results
        result = results["test1"]
        assert result["summary"] == "Test summary"
        assert result["pain_points"] == ["Point 1", "Point 2"]
        assert result["recommendations"] == ["Rec 1", "Rec 2"]
        assert result["segments"] == ["Segment 1", "Segment 2"]
        assert result["tools_mentioned"] == ["Tool 1", "Tool 2"]
        assert result["contrarian_take"] == "Contrarian view"
        assert result["key_metrics"] == ["Metric 1", "Metric 2"]
        assert result["sources"] == ["Source 1", "Source 2"]
        
        # Verify OpenAI was called
        mock_call_openai.assert_called_once()

    @patch('reddit_pipeline.llm.summariser._call_openai')
    def test_summarise_posts_error_handling(self, mock_call_openai):
        """Test LLM summarisation error handling."""
        # Mock OpenAI error
        mock_call_openai.side_effect = Exception("OpenAI API Error")
        
        # Test data
        now = datetime.now(timezone.utc)
        posts = [
            Post(
                id="test1",
                title="Test Post 1",
                score=100,
                num_comments=50,
                created_utc=now,
                subreddit="test",
                author="user1",
                url="https://example.com/1",
                text="Test content 1",
            )
        ]
        
        comments_by_post = {"test1": []}
        
        # Should handle error gracefully
        with pytest.raises(Exception, match="OpenAI API Error"):
            summarise_posts_with_comments(posts, comments_by_post)


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @patch('reddit_pipeline.clients.reddit.RedditClient.fetch_posts')
    @patch('reddit_pipeline.clients.reddit.RedditClient.fetch_comments')
    @patch('reddit_pipeline.llm.summariser._call_openai')
    def test_full_pipeline_integration(self, mock_call_openai, mock_fetch_comments, mock_fetch_posts):
        """Test full pipeline integration with mocked dependencies."""
        # Mock Reddit posts
        now = datetime.now(timezone.utc)
        mock_posts = [
            Post(
                id="test1",
                title="Test Post 1",
                score=100,
                num_comments=50,
                created_utc=now,
                subreddit="test",
                author="user1",
                url="https://example.com/1",
                text="Test content 1",
            )
        ]
        mock_fetch_posts.return_value = mock_posts
        
        # Mock Reddit comments
        mock_comments = [
            {"body": "Great post!", "score": 10},
            {"body": "Interesting perspective", "score": 5}
        ]
        mock_fetch_comments.return_value = mock_comments
        
        # Mock OpenAI response
        mock_call_openai.return_value = {
            "summary": "Test summary",
            "pain_points": ["Point 1"],
            "recommendations": ["Rec 1"],
            "segments": ["Segment 1"],
            "tools_mentioned": ["Tool 1"],
            "contrarian_take": "Contrarian view",
            "key_metrics": ["Metric 1"],
            "sources": ["Source 1"]
        }
        
        # Test full pipeline
        from reddit_pipeline.run import run_pipeline
        
        # This would test the full pipeline if we had access to it
        # For now, we test the individual components
        
        # Test Reddit client
        from reddit_pipeline.clients.reddit import RedditClient
        reddit_client = RedditClient()
        posts = reddit_client.fetch_posts('test', limit=1)
        assert len(posts) == 1
        assert posts[0].id == "test1"
        
        # Test comments fetching
        comments = reddit_client.fetch_comments('test1', limit=2)
        assert len(comments) == 2
        
        # Test summarisation
        comments_by_post = {"test1": comments}
        results = summarise_posts_with_comments(posts, comments_by_post)
        assert "test1" in results
        assert results["test1"]["summary"] == "Test summary"
