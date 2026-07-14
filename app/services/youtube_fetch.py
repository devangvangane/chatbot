import yt_dlp
from typing import List, Dict
from app.config import config
import uuid

class YouTubeService:

    def __init__(self, channel_name: str = config.YOUTUBE_CHANNEL_NAME):
        self.channel_name = channel_name
        self.channel_url = f"https://www.youtube.com/@{channel_name}/videos"

    def get_channel_videos(self) -> List[Dict]:
        """
        Fetch all videos from the YouTube channel.
        """

        videos = []

        channel_options = {
            "extract_flat": True,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(channel_options) as ydl:
            channel_data = ydl.extract_info(
                self.channel_url,
                download=False
            )

        for video in channel_data.get("entries", []):
            video_url = f"https://www.youtube.com/watch?v={video['id']}"

            print(f"Fetching: {video_url}")

            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                details = ydl.extract_info(
                    video_url,
                    download=False
                )

            videos.append({
                "id": str(uuid.uuid4()),
                "title": details.get("title"),
                "description": details.get("description"),
                "url": video_url,
            })

        return videos

    def save_to_json(self, videos: List[Dict], filename: str):
        import json

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(
                videos,
                file,
                indent=4,
                ensure_ascii=False,
            )

if __name__ == "__main__":
    youtube_s = YouTubeService(config.YOUTUBE_CHANNEL_NAME)
    videos = youtube_s.get_channel_videos()
    # youtube_s.save_to_json(videos=videos, filename="youtube_json")
