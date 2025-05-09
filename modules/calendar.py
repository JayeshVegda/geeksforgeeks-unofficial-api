import requests
import json
from typing import Dict, Any, Optional
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Calendar:
    """Calendar class for GeeksForGeeks user submission data"""
    
    BASE_URL = "https://practiceapi.geeksforgeeks.org/api/v1/user/problems/submissions/"
    TIMEOUT = 10  # seconds
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self, username: str, year: Optional[int] = None):
        self.username = username
        self.year = year

    @lru_cache(maxsize=100)
    def fetch_response(self) -> Dict[str, Any]:
        """
        Fetch user submission calendar data
        Returns a dictionary containing submission statistics
        """
        try:
            payload = {
                "handle": self.username,
                "requestType": "getYearwiseUserSubmissions",
                "year": self.year,
                "month": ""
            }

            response = requests.post(
                self.BASE_URL,
                headers=self.HEADERS,
                json=payload,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()

            calendar_info = response.json()
            return self._parse_calendar_data(calendar_info)

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {self.username}: {str(e)}")
            return {"error": f"Request failed: {str(e)}"}
        except ValueError as e:
            logger.error(f"JSON parsing failed for {self.username}: {str(e)}")
            return {"error": f"Failed to parse JSON response: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error for {self.username}: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}

    def _parse_calendar_data(self, calendar_info: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the calendar data from the API response"""
        try:
            if "count" not in calendar_info or "result" not in calendar_info:
                logger.error(f"Unexpected API response format for {self.username}")
                return {"error": "Unexpected API response format"}

            return {
                "Total Submissions": calendar_info["count"],
                "Submission Dates": calendar_info["result"]
            }
        except Exception as e:
            logger.error(f"Error parsing calendar data for {self.username}: {str(e)}")
            return {"error": "Failed to parse calendar data"}