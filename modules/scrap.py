import requests
import json
from bs4 import BeautifulSoup as bs
from functools import lru_cache
from typing import Dict, Any, Optional
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Scraper:
    """Scraper class for GeeksForGeeks user data"""
    
    BASE_URL = "https://auth.geeksforgeeks.org/user/{username}/practice/"
    TIMEOUT = 30  # Increased timeout to 30 seconds
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    def __init__(self, username: str):
        self.username = username
        self.url = self.BASE_URL.format(username=username)
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a session with retry mechanism"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504]  # HTTP status codes to retry on
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetchResponse(self) -> Dict[str, Any]:
        """
        Fetch and parse user data from GeeksForGeeks
        Returns a dictionary containing user information and solved problems
        """
        try:
            logger.info(f"Fetching data for username: {self.username}")
            response = self.session.get(self.url, headers=self.HEADERS, timeout=self.TIMEOUT)
            
            if response.status_code == 404:
                logger.error(f"Profile not found for username: {self.username}")
                return {"error": "Profile not found", "status_code": 404}
            
            response.raise_for_status()
            
            soup = bs(response.content, 'html.parser')
            script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
            
            if not script_tag:
                logger.error(f"Could not find user data for {self.username}")
                return {"error": "Could not find user data", "status_code": 404}

            try:
                user_data = json.loads(script_tag.string)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed for {self.username}: {str(e)}")
                return {"error": "Failed to parse user data", "status_code": 500}

            return self._parse_user_data(user_data)
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out for {self.username}")
            return {"error": "Request timed out", "status_code": 504}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {self.username}: {str(e)}")
            return {"error": f"Request failed: {str(e)}", "status_code": 500}
        except Exception as e:
            logger.error(f"Unexpected error for {self.username}: {str(e)}", exc_info=True)
            return {"error": "An unexpected error occurred", "status_code": 500}
        finally:
            self.session.close()

    def _parse_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the user data from the JSON response"""
        try:
            if "props" not in user_data or "pageProps" not in user_data["props"]:
                logger.error(f"Invalid data structure for {self.username}")
                return {"error": "Invalid data structure", "status_code": 500}

            page_props = user_data["props"]["pageProps"]
            
            if "userInfo" not in page_props:
                logger.error(f"User info not found for {self.username}")
                return {"error": "User info not found", "status_code": 404}

            user_info = page_props["userInfo"]
            user_contest = page_props.get("contestData", {})
            user_contest_data = user_contest.get("user_contest_data", {})
            user_submissions = page_props.get("userSubmissionsInfo", {})

            general_info = self._extract_general_info(user_info, user_contest, user_contest_data)
            solved_stats = self._extract_solved_stats(user_submissions)

            return {
                "info": general_info,
                "solvedStats": solved_stats,
                "status_code": 200
            }
        except KeyError as e:
            logger.error(f"Missing key in user data for {self.username}: {str(e)}")
            return {"error": "Invalid data format", "status_code": 500}
        except Exception as e:
            logger.error(f"Error parsing user data for {self.username}: {str(e)}")
            return {"error": "Failed to parse user data", "status_code": 500}

    def _extract_general_info(self, user_info: Dict[str, Any], 
                            user_contest: Dict[str, Any], 
                            user_contest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract general user information"""
        try:
            return {
                "userName": self.username,
                "fullName": user_info.get("name", ""),
                "profilePicture": user_info.get("profile_image_url", ""),
                "institute": user_info.get("institute_name", ""),
                "instituteRank": user_info.get("institute_rank", ""),
                "longestStreak": user_info.get("pod_solved_longest_streak", "00"),
                "codingScore": user_info.get("score", 0),
                "monthlyScore": user_info.get("monthly_score", 0),
                "currentRating": user_contest_data.get("current_rating", 0),
                "userGlobalRank": user_contest.get("user_global_rank", 0),
                "level": user_contest.get("user_stars", 0),
                "totalProblemsSolved": user_info.get("total_problems_solved", 0),
            }
        except Exception as e:
            logger.error(f"Error extracting general info for {self.username}: {str(e)}")
            return {}

    def _extract_solved_stats(self, user_submissions: Dict[str, Any]) -> Dict[str, Any]:
        """Extract solved problems statistics"""
        try:
            solved_stats = {}
            for difficulty, problems in user_submissions.items():
                questions = [
                    {
                        "question": details.get("pname", ""),
                        "questionUrl": f"https://practice.geeksforgeeks.org/problems/{details.get('slug', '')}"
                    }
                    for details in problems.values()
                ]
                solved_stats[difficulty.lower()] = {
                    "count": len(questions),
                    "questions": questions
                }
            return solved_stats
        except Exception as e:
            logger.error(f"Error extracting solved stats for {self.username}: {str(e)}")
            return {}