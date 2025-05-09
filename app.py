from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from modules.scrap import Scraper
from modules.calendar import Calendar
from modules.contest import Contest
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

# Configuration
RATE_LIMIT_PER_MINUTE = "10 per minute"
RATE_LIMIT_PER_HOUR = "50 per hour"
RATE_LIMIT_PER_DAY = "200 per day"

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT_PER_DAY, RATE_LIMIT_PER_HOUR],
    storage_uri="memory://"
)

def validate_username(username):
    """Validate username format"""
    if not username or not isinstance(username, str):
        return False
    # Username should be alphanumeric with underscores and hyphens
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', username))

def validate_year(year):
    """Validate year format"""
    if not year:
        return True
    try:
        year = int(year)
        current_year = datetime.now().year
        return 2000 <= year <= current_year
    except ValueError:
        return False

# Custom error handler for rate limiting
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Too many requests",
        "message": "Rate limit exceeded. Please try again in a minute.",
        "status_code": 429
    }), 429

# Custom error handler for 404
@app.errorhandler(404)
def not_found_handler(e):
    return jsonify({
        "error": "Not Found",
        "message": "The requested resource was not found.",
        "status_code": 404
    }), 404

# Custom error handler for 500
@app.errorhandler(500)
def internal_error_handler(e):
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later.",
        "status_code": 500
    }), 500

class geeksforgeeksAPI(Resource):
    @limiter.limit(RATE_LIMIT_PER_MINUTE)
    def get(self, username):
        try:
            if not validate_username(username):
                return {"error": "Invalid username format", "status_code": 400}, 400
            
            logger.info(f"Processing request for username: {username}")
            scraper = Scraper(username)
            response = scraper.fetchResponse()
            
            if "error" in response:
                status_code = response.get("status_code", 500)
                return response, status_code
                
            return response, 200
            
        except Exception as e:
            logger.error(f"Error processing request for {username}: {str(e)}")
            return {"error": "Internal Server Error", "status_code": 500}, 500

class GeeksForGeeksCalendarAPI(Resource):
    @limiter.limit(RATE_LIMIT_PER_MINUTE)
    def get(self, username):
        try:
            if not validate_username(username):
                return {"error": "Invalid username format", "status_code": 400}, 400

            # Get year from query parameters
            year = request.args.get('year')
            if year:
                if not validate_year(year):
                    return {"error": "Invalid year format", "status_code": 400}, 400
                year = int(year)
            else:
                year = datetime.now().year

            logger.info(f"Processing calendar request for username: {username}, year: {year}")
            calendar_obj = Calendar(username, year)
            response = calendar_obj.fetch_response()
            
            if "error" in response:
                status_code = response.get("status_code", 500)
                return response, status_code
                
            return response, 200
            
        except Exception as e:
            logger.error(f"Error processing calendar request for {username}: {str(e)}")
            return {"error": "Internal Server Error", "status_code": 500}, 500

class GeeksForGeeksContestAPI(Resource):
    @limiter.limit(RATE_LIMIT_PER_MINUTE)
    def get(self, username):
        try:
            if not validate_username(username):
                return {"error": "Invalid username format", "status_code": 400}, 400

            # Get year from query parameters
            year = request.args.get('year')
            if year:
                if not validate_year(year):
                    return {"error": "Invalid year format", "status_code": 400}, 400
                year = int(year)
            else:
                year = datetime.now().year

            logger.info(f"Processing contest request for username: {username}, year: {year}")
            contest_obj = Contest(username, year)
            response = contest_obj.fetch_response()
            
            if "error" in response:
                status_code = response.get("status_code", 500)
                return response, status_code
                
            return response, 200
            
        except Exception as e:
            logger.error(f"Error processing contest request for {username}: {str(e)}")
            return {"error": "Internal Server Error", "status_code": 500}, 500

# API Routes
api.add_resource(geeksforgeeksAPI, "/<string:username>")
api.add_resource(GeeksForGeeksCalendarAPI, "/<string:username>/calendar")
api.add_resource(GeeksForGeeksContestAPI, "/<string:username>/contest")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)  # Set debug=True for development