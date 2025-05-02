import requests
import json
import base64
import math
import time
import traceback
PROXY_SERVER = "geo.iproyal.com:12321"
PROXY_USER = "jxuQHPGrydd0jIva"
PROXY_PASS = "RU7veaFCDR0nRHbL"

# Format proxy with credentials
proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_SERVER}"

proxies = {
    "http": proxy_url,
    "https": proxy_url,
}
MAX_RETRIES = 5
INITIAL_BACKOFF = 2  # seconds

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
    
    headers = clean_headers(headers)
    backoff = INITIAL_BACKOFF

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"🔁 Attempt {attempt} for offset {offset}...")
            response = requests.post(
                "https://www.yelp.com/gql/batch",
                headers=headers,
                data=payload,
                proxies=proxies,
                timeout=15  # Optional: avoid hanging forever
            )
            response.raise_for_status()
            print("✅ Success")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed (attempt {attempt}):", e)
            traceback.print_exc()
            if attempt < MAX_RETRIES:
                print(f"⏳ Retrying in {backoff} seconds...")
                time.sleep(backoff)
                backoff *= 2
            else:
                print("🚫 Max retries reached. Giving up.")
                print("📦 Payload:", payload)
                print("📬 Headers:", headers)
                return None
def clean_headers(headers):
    cleaned = {}
    for k, v in headers.items():
        try:
            cleaned[k] = v.encode('latin-1').decode('latin-1')
        except UnicodeEncodeError:
            print(f"⚠️ Skipping non-latin header: {k} => {v}")
    return cleaned
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
    # print(main_data)
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

    print(f"🎉 Final merged data saved and returned")
    # return final_output

