"""
YouTube API Integration Tests - Iteration 26
Tests for /api/youtube/videos, /api/youtube/live, /api/youtube/channel endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
KAIZER_NIGHA_CHANNEL_ID = "UCTDsrLjZs9otGHBm4YoEK-A"


class TestYouTubeVideos:
    """Tests for /api/youtube/videos endpoint"""

    def test_get_videos_success(self):
        """GET /api/youtube/videos should return videos from Kaizer Nigha channel"""
        response = requests.get(f"{BASE_URL}/api/youtube/videos")
        assert response.status_code == 200
        
        data = response.json()
        assert "videos" in data
        assert "total" in data
        assert isinstance(data["videos"], list)
        assert data["total"] > 0
        print(f"PASS: Got {data['total']} videos from channel")

    def test_videos_have_required_fields(self):
        """Each video should have id, title, thumbnail, published_at"""
        response = requests.get(f"{BASE_URL}/api/youtube/videos?max_results=3")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["videos"]) > 0
        
        for video in data["videos"]:
            assert "id" in video, "Video missing 'id' field"
            assert "title" in video, "Video missing 'title' field"
            assert "thumbnail" in video, "Video missing 'thumbnail' field"
            assert "published_at" in video, "Video missing 'published_at' field"
            assert len(video["id"]) == 11, f"Video ID should be 11 chars: {video['id']}"
            assert video["thumbnail"].startswith("https://"), "Thumbnail should be HTTPS URL"
        print(f"PASS: All {len(data['videos'])} videos have required fields")

    def test_videos_from_kaizer_nigha_channel(self):
        """Videos should be from Kaizer Nigha channel"""
        response = requests.get(f"{BASE_URL}/api/youtube/videos?max_results=5")
        assert response.status_code == 200
        
        data = response.json()
        for video in data["videos"]:
            channel_title = video.get("channel_title", "")
            assert "Kaizer" in channel_title or channel_title == "Kaizer Nigha", \
                f"Expected Kaizer Nigha channel, got: {channel_title}"
        print("PASS: All videos are from Kaizer Nigha channel")

    def test_max_results_parameter(self):
        """max_results parameter should limit number of videos returned"""
        response = requests.get(f"{BASE_URL}/api/youtube/videos?max_results=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["videos"]) <= 5
        print(f"PASS: max_results=5 returned {len(data['videos'])} videos")

    def test_custom_channel_id_parameter(self):
        """channel_id parameter should allow querying different channels"""
        response = requests.get(f"{BASE_URL}/api/youtube/videos?channel_id={KAIZER_NIGHA_CHANNEL_ID}&max_results=2")
        assert response.status_code == 200
        
        data = response.json()
        assert "videos" in data
        print("PASS: channel_id parameter works correctly")


class TestYouTubeLive:
    """Tests for /api/youtube/live endpoint"""

    def test_get_live_streams(self):
        """GET /api/youtube/live should return live stream status"""
        response = requests.get(f"{BASE_URL}/api/youtube/live")
        assert response.status_code == 200
        
        data = response.json()
        assert "is_live" in data, "Response missing 'is_live' boolean"
        assert "streams" in data, "Response missing 'streams' array"
        assert isinstance(data["is_live"], bool)
        assert isinstance(data["streams"], list)
        print(f"PASS: Live endpoint returned is_live={data['is_live']}, {len(data['streams'])} streams")

    def test_live_streams_structure(self):
        """Live streams (if any) should have proper structure"""
        response = requests.get(f"{BASE_URL}/api/youtube/live")
        assert response.status_code == 200
        
        data = response.json()
        if data["streams"]:
            for stream in data["streams"]:
                assert "id" in stream
                assert "title" in stream
                assert "thumbnail" in stream
                assert stream.get("is_live") == True
            print(f"PASS: {len(data['streams'])} live streams have correct structure")
        else:
            print("PASS: No live streams currently, is_live=false as expected")

    def test_live_with_custom_channel_id(self):
        """channel_id parameter should work for live endpoint"""
        response = requests.get(f"{BASE_URL}/api/youtube/live?channel_id={KAIZER_NIGHA_CHANNEL_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert "is_live" in data
        print("PASS: channel_id parameter works for live endpoint")


class TestYouTubeChannel:
    """Tests for /api/youtube/channel endpoint"""

    def test_get_channel_info(self):
        """GET /api/youtube/channel should return channel info"""
        response = requests.get(f"{BASE_URL}/api/youtube/channel")
        assert response.status_code == 200
        
        data = response.json()
        assert "channel" in data
        assert data["channel"] is not None
        print("PASS: Channel info retrieved successfully")

    def test_channel_is_kaizer_nigha(self):
        """Channel title should be Kaizer Nigha"""
        response = requests.get(f"{BASE_URL}/api/youtube/channel")
        assert response.status_code == 200
        
        data = response.json()
        channel = data["channel"]
        assert channel["title"] == "Kaizer Nigha", f"Expected 'Kaizer Nigha', got '{channel['title']}'"
        print("PASS: Channel title is 'Kaizer Nigha'")

    def test_channel_has_statistics(self):
        """Channel should have subscriber_count, video_count, view_count"""
        response = requests.get(f"{BASE_URL}/api/youtube/channel")
        assert response.status_code == 200
        
        data = response.json()
        channel = data["channel"]
        
        assert "subscriber_count" in channel
        assert "video_count" in channel
        assert "view_count" in channel
        
        assert isinstance(channel["subscriber_count"], int)
        assert isinstance(channel["video_count"], int)
        assert isinstance(channel["view_count"], int)
        
        assert channel["subscriber_count"] > 0, "Subscriber count should be > 0"
        assert channel["video_count"] > 0, "Video count should be > 0"
        assert channel["view_count"] > 0, "View count should be > 0"
        
        print(f"PASS: Channel stats - {channel['subscriber_count']:,} subs, {channel['video_count']:,} videos, {channel['view_count']:,} views")

    def test_channel_has_thumbnail(self):
        """Channel should have thumbnail URL"""
        response = requests.get(f"{BASE_URL}/api/youtube/channel")
        assert response.status_code == 200
        
        data = response.json()
        channel = data["channel"]
        
        assert "thumbnail" in channel
        assert channel["thumbnail"].startswith("https://")
        print("PASS: Channel has valid thumbnail URL")

    def test_channel_id_matches(self):
        """Channel ID should match Kaizer Nigha channel ID"""
        response = requests.get(f"{BASE_URL}/api/youtube/channel")
        assert response.status_code == 200
        
        data = response.json()
        channel = data["channel"]
        
        assert channel["id"] == KAIZER_NIGHA_CHANNEL_ID, \
            f"Expected {KAIZER_NIGHA_CHANNEL_ID}, got {channel['id']}"
        print("PASS: Channel ID matches Kaizer Nigha")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
