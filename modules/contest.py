import requests
import json
import base64
from typing import Dict, Any, Optional
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Contest:
    """Contest class for GeeksForGeeks user contest data"""
    
    BASE_URL = "https://practiceapi.geeksforgeeks.org/api/v1/rating/{username}/info"
    TIMEOUT = 10  # seconds
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self, username: str, year: Optional[int] = None):
        self.username = username
        self.year = year
        self.url = self.BASE_URL.format(
            username=base64.b64encode(username.encode()).decode()
        )

    @lru_cache(maxsize=100)
    def fetch_response(self) -> Dict[str, Any]:
        try:
            payload = {"year": self.year}
            
            response = requests.post(
                self.url,
                headers=self.HEADERS,
                params=payload,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()

            contest_info = response.json()
            return self._parse_contest_data(contest_info)

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {self.username}: {str(e)}")
            return {"error": f"Request failed: {str(e)}"}
        except ValueError as e:
            logger.error(f"JSON parsing failed for {self.username}: {str(e)}")
            return {"error": f"Failed to parse JSON response: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error for {self.username}: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}

    def _parse_contest_data(self, contest_info: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the contest data from the API response"""
        try:
            if "user_global_rank" not in contest_info or "star_colour_codes" not in contest_info:
                logger.error(f"Unexpected API response format for {self.username}")
                return {"error": "Unexpected API response format"}

            contest_data = {
                "Level": contest_info["user_stars"],
                "Rank": contest_info["user_contest_data"]["current_rating"],
                "Global Rank": contest_info["user_global_rank"],
                "Total Contests": contest_info["user_contest_data"]["no_of_participated_contest"],
            }

            return {
                "Contest Data": contest_data,
                "Contest Details": contest_info["user_contest_data"]["contest_data"]
            }
        except Exception as e:
            logger.error(f"Error parsing contest data for {self.username}: {str(e)}")
            return {"error": "Failed to parse contest data"}