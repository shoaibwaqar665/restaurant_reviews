import requests
import json
import base64
import math

def get_reviews_response(enc_biz_id, offset, headers):
    after = base64.b64encode(json.dumps({
        "version": 1,
        "type": "offset",
        "offset": offset
    }).encode('utf-8')).decode('utf-8')

    payload = json.dumps([
        {
            "operationName": "GetBusinessReviewFeed",
            "variables": {
                "encBizId": enc_biz_id,
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

    response = requests.post("https://www.yelp.com/gql/batch", headers=headers, data=payload)
    response.raise_for_status()
    return response.json()

def scrape_yelp_reviews(enc_biz_id, pages, output_file):

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

    # Start scraping
    print("🚀 Starting Yelp review scraping...")
    offset = 0
    main_response = get_reviews_response(enc_biz_id, offset, headers)
    main_data = main_response[0]
    review_list = main_data["data"]["business"]["reviews"]["edges"]
    total_pages = pages/20
    total_pages = math.ceil(total_pages)
    print(f"Total pages to scrape: {total_pages}")
    for i in range(1, total_pages):
        offset = i * 20
        try:
            next_response = get_reviews_response(enc_biz_id, offset, headers)
            next_edges = next_response[0]["data"]["business"]["reviews"]["edges"]
            review_list.extend(next_edges)
            print(f"✅ Appended reviews from offset {offset}")
        except Exception as e:
            print(f"❌ Error at offset {offset}: {e}")
            break

    final_output = {
        "offset": 0,
        "reviews": [main_data]
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

    print(f"🎉 Final merged data saved in {output_file}")

# # Example usage:
if __name__ == "__main__":
    scrape_yelp_reviews(enc_biz_id="tuWl2S2O4YwI2qHXiIaSyw", pages=328, output_file="reviews_yelp.json")
