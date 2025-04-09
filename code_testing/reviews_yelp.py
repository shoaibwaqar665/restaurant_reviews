import requests
import json

url = "https://www.yelp.com/gql/batch"

# Load cookies from file
with open("yelp_cookies.txt", "r") as f:
    cookies = f.read().strip()

payload = json.dumps([
  {
    "operationName": "GetBusinessReviewFeed",
    "variables": {
      "encBizId": "tuWl2S2O4YwI2qHXiIaSyw",
      "reviewsPerPage": 20,
      "selectedReviewEncId": "",
      "hasSelectedReview": False,
      "sortBy": "RELEVANCE_DESC",
      "languageCode": "en",
      "ratings": [5, 4, 3, 2, 1],
      "queryText": "",
      "isSearching": False,
      "after": "eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0IjoxOX0=",
      "isTranslating": False,
      "translateLanguageCode": "en",
      "reactionsSourceFlow": "businessPageReviewSection",
      "guv": "CFCAA4676196EA17",
      "minConfidenceLevel": "HIGH_CONFIDENCE",
      "highlightType": "",
      "highlightIdentifier": "",
      "isHighlighting": False
    },
    "extensions": {
      "operationType": "query",
      "documentId": "691087a117482fc6d72e9549a7a23834bc35f578b0c161319eb1f9b20c0d92c0"
    }
  }
])

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Encoding': 'gzip, deflate, br',  # <- this tells server to compress, and requests auto-decompresses
    'x-apollo-operation-name': 'GetBusinessReviewFeed',
    'Content-Type': 'application/json',
    'Cookie': cookies  # <- use the one loaded from file
}

response = requests.post(url, headers=headers, data=payload)

# Make sure content is decompressed and parsed
try:
    json_data = response.json()
    print(json.dumps(json_data, indent=2))
    
        # Save to file
    with open("reviews_yelp.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(json_data)} reviews saved to reviews_yelp.json")
    
except Exception:
    print("Standard JSON parse failed, trying manual decoding...")
    