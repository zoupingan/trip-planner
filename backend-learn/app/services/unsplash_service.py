import requests

from app.config import get_settings


class UnsplashService:
    def __init__(self):
        settings = get_settings()
        self.access_key = settings.unsplash_access_key
        self.base_url = "https://api.unsplash.com"

    def search_photos(self, query: str, per_page: int = 5):
        try:
            url = f"{self.base_url}/search/photos"
            params = {
                "query": query,
                "per_page": per_page,
                "client_id": self.access_key,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            photos = []
            for photo in results:
                photos.append(
                    {
                        "id": photo.get("id"),
                        "url": photo.get("urls", {}).get("regular"),
                        "thumb": photo.get("urls", {}).get("thumb"),
                        "description": photo.get("description") or photo.get("alt_description"),
                        "photographer": photo.get("user", {}).get("name"),
                    }
                )
            return photos
        except Exception as e:
            print(f"Unsplash 搜索失败: {e}")
            return []

    def get_photo_url(self, query: str):
        photos = self.search_photos(query)
        if photos:
            return photos[0]["url"]
        return None

unsplash_service = UnsplashService()

def get_unsplash() -> UnsplashService:
    return unsplash_service
