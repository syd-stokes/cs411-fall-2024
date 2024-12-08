import logging
import requests
from typing import List, Dict

from movie_collection.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class TMDbAPI:
    """
    A class to interact with The Movie Database (TMDb) API.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.themoviedb.org/3"):
        """
        Initializes the TMDbAPI class.

        Args:
            api_key (str): TMDb API key for authentication.
            base_url (str): The base URL for TMDb API endpoints.
        """
        self.api_key = api_key
        self.base_url = base_url

    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Makes a GET request to the TMDb API.

        Args:
            endpoint (str): API endpoint.
            params (dict): Query parameters.

        Returns:
            dict: JSON response.

        Raises:
            RuntimeError: If the request fails.
        """
        url = f"{self.base_url}/{endpoint}"
        params["api_key"] = self.api_key

        try:
            logger.info("Making request to TMDb API: %s with params %s", url, params)
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("TMDb API request failed: %s", e)
            raise RuntimeError(f"TMDb API request failed: {e}")

    def get_movies_by_director(self, director_name: str) -> List[Dict]:
        """
        Fetches movies directed by a specific director.

        Args:
            director_name (str): Director's name.

        Returns:
            list: List of movies directed by the specified director.
        """
        logger.info("Fetching movies for director: %s", director_name)
        response = self._make_request("search/person", {"query": director_name})
        movies = []

        for person in response.get("results", []):
            if person.get("name") == director_name and "known_for" in person:
                for movie in person["known_for"]:
                    if movie.get("media_type") == "movie":
                        movies.append({
                            "title": movie.get("title"),
                            "release_date": movie.get("release_date"),
                            "rating": movie.get("vote_average"),
                            "overview": movie.get("overview"),
                        })

        return movies

    def get_top_rated_movies(self) -> List[Dict]:
        """
        Fetches top-rated movies.

        Returns:
            list: List of top-rated movies.
        """
        logger.info("Fetching top-rated movies.")
        response = self._make_request("movie/top_rated", {})
        return [
            {
                "title": movie["title"],
                "release_date": movie.get("release_date"),
                "rating": movie.get("vote_average"),
                "overview": movie.get("overview"),
            }
            for movie in response.get("results", [])
        ]

    def search_movie_by_title(self, title: str) -> List[Dict]:
        """
        Searches for movies by title.

        Args:
            title (str): Movie title.

        Returns:
            list: List of movies matching the title.
        """
        logger.info("Searching for movies with title: %s", title)
        response = self._make_request("search/movie", {"query": title})
        return [
            {
                "title": movie["title"],
                "release_date": movie.get("release_date"),
                "rating": movie.get("vote_average"),
                "overview": movie.get("overview"),
            }
            for movie in response.get("results", [])
        ]

    def get_movie_details(self, movie_id: int) -> Dict:
        """
        Fetches details for a specific movie.

        Args:
            movie_id (int): TMDb movie ID.

        Returns:
            dict: Detailed information about the movie.
        """
        logger.info("Fetching details for movie ID: %d", movie_id)
        response = self._make_request(f"movie/{movie_id}", {})
        return {
            "title": response.get("title"),
            "release_date": response.get("release_date"),
            "rating": response.get("vote_average"),
            "overview": response.get("overview"),
            "genres": [genre["name"] for genre in response.get("genres", [])],
        }

