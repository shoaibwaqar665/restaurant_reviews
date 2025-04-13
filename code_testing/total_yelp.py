import requests
import json
import base64

url = "https://www.yelp.com/gql/batch"

# Load cookies from file
with open("yelp_cookies.txt", "r") as f:
    cookies = f.read().strip()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'x-apollo-operation-name': 'GetBusinessReviewFeed',
    'Content-Type': 'application/json',
    'Cookie': cookies
}

# Function to get response with a given offset
def get_reviews_response(offset):
    after = base64.b64encode(json.dumps({
        "version": 1,
        "type": "offset",
        "offset": offset
    }).encode('utf-8')).decode('utf-8')

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
                "after": after,
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

    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


# Get first response
offset = 0
first_response = get_reviews_response(offset)
main_data = first_response[0]

# Reference to the main review list
review_list = main_data["data"]["business"]["reviews"]["edges"]

# Append additional reviews
for i in range(1, 18):  # Total: 18 * 20 = 360 reviews
    offset = i * 20
    try:
        next_response = get_reviews_response(offset)
        next_edges = next_response[0]["data"]["business"]["reviews"]["edges"]
        review_list.extend(next_edges)
        print(f"✅ Appended reviews from offset {offset}")
    except Exception as e:
        print(f"❌ Error at offset {offset}: {e}")
        break

# Wrap into desired format
final_output = {
    "offset": 0,
    "reviews": [main_data]
}

# Save result
with open("reviews_yelp.json", "w", encoding="utf-8") as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

print("🎉 Final merged data saved in reviews_yelp.json")
