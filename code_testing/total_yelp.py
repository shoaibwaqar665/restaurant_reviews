import requests
import json
import base64

url = "https://www.yelp.com/gql/batch"

# Load cookies from file
with open("yelp_cookies.txt", "r") as f:
    cookies = f.read().strip()

# Initial payload with offset = 0
offset = 0

# Open the file in append mode
with open("reviews_yelp.json", "a", encoding="utf-8") as f:
    i=0
    while True:
        # Encode the current offset into base64
        after = base64.b64encode(json.dumps({
            "version": 1,
            "type": "offset",
            "offset": offset
        }).encode('utf-8')).decode('utf-8')

        # Update the payload with the new "after" value
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

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'x-apollo-operation-name': 'GetBusinessReviewFeed',
            'Content-Type': 'application/json',
            'Cookie': cookies  # use the one loaded from file
        }

        response = requests.post(url, headers=headers, data=payload)

        try:
            json_data = response.json()
            # reviews = json_data.get('data', {}).get('business', {}).get('reviews', {}).get('reviews', [])

            # if not reviews:
            #     break  # No more reviews

            # Save the reviews to the file according to their offset
            json.dump({"offset": offset, "reviews": json_data}, f, ensure_ascii=False, indent=2)
            f.write("\n")  # Adding a newline for separation between different offset entries

            print(f"Fetched {len(json_data)} reviews at offset {offset}")

            # Extract the new offset value (next 'after' parameter)
            # after_value = json_data.get('data', {}).get('business', {}).get('reviews', {}).get('pageInfo', {}).get('endCursor', None)
            
            # if not after_value:
            #     break  # No more pages, end the loop

            # Update the offset for the next request
            offset += 20  # Increment by the reviewsPerPage
            i += 1
            if i > 17:
                break

        except Exception as e:
            print(f"Error: {e}")
            break

print("✅ All reviews saved to reviews_yelp.json")
