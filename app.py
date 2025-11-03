from flask import Flask, jsonify, request, render_template_string
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
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

# Configuration
RATE_LIMIT_PER_MINUTE = "10 per minute"
RATE_LIMIT_PER_HOUR = "50 per hour"
RATE_LIMIT_PER_DAY = "200 per day"

# Initialize rate limiter with memory storage for Vercel
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT_PER_DAY, RATE_LIMIT_PER_HOUR],
    storage_uri="memory://",
    strategy="fixed-window",  # Use fixed window strategy for better serverless compatibility
    default_limits_exempt_when=lambda: True  # Disable rate limiting in development
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

# Welcome/Documentation Route
@app.route("/", methods=["GET"])
def welcome():
    """
    Welcome endpoint that provides API documentation
    """
    api_info = {
        "name": "GeeksForGeeks Unofficial API",
        "description": "An unofficial API to fetch GeeksForGeeks user profiles, contest data, and calendar information",
        "version": "1.0.0",
        "endpoints": {
            "user_profile": {
                "url": "/{username}",
                "method": "GET",
                "description": "Get user profile information",
                "example": "/john_doe"
            },
            "calendar": {
                "url": "/{username}/calendar",
                "method": "GET",
                "description": "Get user's activity calendar",
                "parameters": {
                    "year": "optional - specific year (default: current year)"
                },
                "example": "/john_doe/calendar?year=2024"
            },
            "contest": {
                "url": "/{username}/contest",
                "method": "GET",
                "description": "Get user's contest participation data",
                "parameters": {
                    "year": "optional - specific year (default: current year)"
                },
                "example": "/john_doe/contest?year=2024"
            }
        },
        "rate_limits": {
            "per_minute": "10 requests",
            "per_hour": "50 requests",
            "per_day": "200 requests"
        },
        "response_format": "JSON",
        "support": {
            "github": "https://github.com/JayeshVegda/geeksforgeeks-unofficial-api",
            "documentation": "https://github.com/JayeshVegda/geeksforgeeks-unofficial-api#readme"
        }
    }
    
    # Check if client wants JSON response
    if request.headers.get('Accept', '').find('application/json') != -1 or \
       request.args.get('format') == 'json':
        return jsonify(api_info), 200
    
    # Get the base URL dynamically
    base_url = request.url_root.rstrip('/')
    
    # Return HTML page for browser clients
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeeksForGeeks Unofficial API</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.95;
        }
        .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        .content {
            padding: 40px 30px;
        }
        .section {
            margin-bottom: 35px;
        }
        .section h2 {
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 15px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .endpoint-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .endpoint-card:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .endpoint-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
        }
        .method-badge {
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 0.9em;
        }
        .url {
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            color: #764ba2;
            font-weight: bold;
        }
        .description {
            color: #555;
            margin-bottom: 10px;
        }
        .example {
            background: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
        }
        .params {
            margin-top: 10px;
            padding-left: 20px;
        }
        .params li {
            margin-bottom: 5px;
            color: #555;
        }
        .rate-limit {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .rate-limit h3 {
            color: #856404;
            margin-bottom: 10px;
        }
        .rate-limit ul {
            list-style: none;
            padding: 0;
        }
        .rate-limit li {
            padding: 5px 0;
            color: #856404;
        }
        .rate-limit li::before {
            content: "⚡ ";
            font-size: 1.2em;
        }
        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #dee2e6;
        }
        .footer a {
            color: #667eea;
            text-decoration: none;
            margin: 0 15px;
            font-weight: bold;
            transition: color 0.2s;
        }
        .footer a:hover {
            color: #764ba2;
            text-decoration: underline;
        }
        .try-it {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            margin-top: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .try-it:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 GeeksForGeeks Unofficial API</h1>
            <p>Your gateway to GeeksForGeeks data</p>
            <span class="badge">Version 1.0.0</span>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📚 API Endpoints</h2>
                
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method-badge">GET</span>
                        <span class="url">/{username}</span>
                    </div>
                    <div class="description">
                        Get comprehensive user profile information including solved problems, coding practice data, and achievements.
                    </div>
                    <div class="example">
                        Example: <span style="color: #98c379;">{base_url}/john_doe</span>
                    </div>
                </div>
                
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method-badge">GET</span>
                        <span class="url">/{username}/calendar</span>
                    </div>
                    <div class="description">
                        Retrieve user's activity calendar showing coding activity over time.
                    </div>
                    <div class="params">
                        <strong>Optional Parameters:</strong>
                        <ul>
                            <li><code>year</code> - Specific year (default: current year)</li>
                        </ul>
                    </div>
                    <div class="example">
                        Example: <span style="color: #98c379;">{base_url}/john_doe/calendar?year=2024</span>
                    </div>
                </div>
                
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method-badge">GET</span>
                        <span class="url">/{username}/contest</span>
                    </div>
                    <div class="description">
                        Get user's contest participation history and performance statistics.
                    </div>
                    <div class="params">
                        <strong>Optional Parameters:</strong>
                        <ul>
                            <li><code>year</code> - Specific year (default: current year)</li>
                        </ul>
                    </div>
                    <div class="example">
                        Example: <span style="color: #98c379;">{base_url}/john_doe/contest?year=2024</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>⚡ Rate Limits</h2>
                <div class="rate-limit">
                    <h3>Please respect the following rate limits:</h3>
                    <ul>
                        <li><strong>10 requests</strong> per minute</li>
                        <li><strong>50 requests</strong> per hour</li>
                        <li><strong>200 requests</strong> per day</li>
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2>🔧 Response Format</h2>
                <p>All responses are returned in JSON format with appropriate HTTP status codes.</p>
                <button class="try-it" onclick="window.location.href='?format=json'">
                    View API Info as JSON
                </button>
            </div>
        </div>
        
        <div class="footer">
            <p>Made with ❤️ for the developer community</p>
            <div style="margin-top: 15px;">
                <a href="https://github.com/JayeshVegda/geeksforgeeks-unofficial-api" target="_blank">📦 GitHub</a>
                <a href="https://github.com/JayeshVegda/geeksforgeeks-unofficial-api#readme" target="_blank">📖 Documentation</a>
            </div>
        </div>
    </div>
</body>
</html>
    """
    return render_template_string(html_template)

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
                logger.error(f"Error in response for {username}: {response['error']}")
                return response, status_code
                
            return response, 200
            
        except Exception as e:
            logger.error(f"Error processing request for {username}: {str(e)}", exc_info=True)
            return {"error": "Internal Server Error", "message": str(e), "status_code": 500}, 500

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

# Add this at the end of the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))