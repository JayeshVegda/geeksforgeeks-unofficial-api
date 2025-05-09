# GeeksForGeeks API


<div align="center">
 <img src="https://images.yourstory.com/cs/images/companies/119169043101580097794440231905187057223611079n-1617083628661.png" width = "33%"  >
</div>
<br>
A RESTful API service that provides access to GeeksForGeeks user data, including profile information, solved problems, contest history, and submission calendar.

## API URL

The API is now live and can be accessed at:
```
https://mygfg-api.vercel.app
```

## API Endpoints Table

| Endpoint | Method | Description | Parameters | Example |
|----------|--------|-------------|------------|---------|
| `/<username>` | GET | Get user profile and solved problems | `username` (path) | `https://mygfg-api.vercel.app/username123` |
| `/<username>/calendar` | GET | Get user's submission calendar | `username` (path)<br>`year` (query, optional) | `https://mygfg-api.vercel.app/username123/calendar?year=2024` |
| `/<username>/contest` | GET | Get user's contest history | `username` (path)<br>`year` (query, optional) | `https://mygfg-api.vercel.app/username123/contest?year=2024` |

### Response Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Invalid username format or year |
| 404 | User profile not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

## Features

- **User Profile Data**: Get detailed information about a GeeksForGeeks user
- **Solved Problems**: Access user's solved problems categorized by difficulty
- **Contest History**: View user's contest participation and ratings
- **Submission Calendar**: Track user's coding activity over time
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Error Handling**: Comprehensive error handling and meaningful error messages

## API Endpoints

### 1. User Profile
```
GET https://mygfg-api.vercel.app/<username>
```
Returns user's profile information and solved problems.

**Example:**
```
https://mygfg-api.vercel.app/username123
```

**Example Response:**
```json
{
    "info": {
        "userName": "example_user",
        "fullName": "Example User",
        "profilePicture": "https://...",
        "institute": "Example Institute",
        "instituteRank": "1",
        "longestStreak": "30",
        "codingScore": 1500,
        "monthlyScore": 500,
        "currentRating": 1800,
        "userGlobalRank": 100,
        "level": 5,
        "totalProblemsSolved": 200
    },
    "solvedStats": {
        "easy": {
            "count": 100,
            "questions": [...]
        },
        "medium": {
            "count": 80,
            "questions": [...]
        },
        "hard": {
            "count": 20,
            "questions": [...]
        }
    }
}
```

### 2. Submission Calendar
```
GET https://mygfg-api.vercel.app/<username>/calendar?year=2024
```
Returns user's submission activity for the specified year.

**Example:**
```
https://mygfg-api.vercel.app/username123/calendar?year=2024
```

**Query Parameters:**
- `year` (optional): Year to fetch submissions for (defaults to current year)

**Example Response:**
```json
{
    "Total Submissions": 150,
    "Submission Dates": {
        "2024-01-01": 5,
        "2024-01-02": 3,
        ...
    }
}
```

### 3. Contest History
```
GET https://mygfg-api.vercel.app/<username>/contest?year=2024
```
Returns user's contest participation and ratings.

**Example:**
```
https://mygfg-api.vercel.app/username123/contest?year=2024
```

**Query Parameters:**
- `year` (optional): Year to fetch contest data for (defaults to current year)

**Example Response:**
```json
{
    "Contest Data": {
        "Level": 5,
        "Rank": 1800,
        "Global Rank": 100,
        "Total Contests": 20
    },
    "Contest Details": [...]
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:
- 10 requests per minute per IP
- 50 requests per hour per IP
- 200 requests per day per IP

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/geeksforgeeks-api.git
cd geeksforgeeks-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the Flask server:
```bash
python app.py
```

The server will start at `http://localhost:5000`

## Project Structure

```
geeksforgeeks-api/
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
├── README.md          # Project documentation
└── modules/
    ├── scrap.py       # User profile scraper
    ├── calendar.py    # Submission calendar handler
    └── contest.py     # Contest data handler
```

## Dependencies

- Flask
- Flask-RESTful
- Flask-Limiter
- Requests
- BeautifulSoup4

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input parameters
- `404 Not Found`: User profile not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Your Name - [@yourusername](https://github.com/yourusername)

## Acknowledgments

- GeeksForGeeks for providing the platform
- Flask and its extensions for the web framework
- All contributors who have helped improve this project
