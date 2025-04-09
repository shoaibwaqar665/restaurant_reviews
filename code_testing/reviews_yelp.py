# import requests
# import json
# import base64

# url = "https://www.yelp.com/gql/batch"

# # Load cookies from file
# with open("yelp_cookies.txt", "r") as f:
#     cookies = f.read().strip()

# offset = 0
# after = base64.b64encode(json.dumps({
#             "version": 1,
#             "type": "offset",
#             "offset": offset
#         }).encode('utf-8')).decode('utf-8')
# payload = json.dumps([
#   {
#     "operationName": "GetBusinessReviewFeed",
#     "variables": {
#       "encBizId": "tuWl2S2O4YwI2qHXiIaSyw",
#       "reviewsPerPage": 40,
#       "selectedReviewEncId": "",
#       "hasSelectedReview": False,
#       "sortBy": "RELEVANCE_DESC",
#       "languageCode": "en",
#       "ratings": [5, 4, 3, 2, 1],
#       "queryText": "",
#       "isSearching": False,
#       "after": after,
#       "isTranslating": False,
#       "translateLanguageCode": "en",
#       "reactionsSourceFlow": "businessPageReviewSection",
#       "guv": "CFCAA4676196EA17",
#       "minConfidenceLevel": "HIGH_CONFIDENCE",
#       "highlightType": "",
#       "highlightIdentifier": "",
#       "isHighlighting": False
#     },
#     "extensions": {
#       "operationType": "query",
#       "documentId": "691087a117482fc6d72e9549a7a23834bc35f578b0c161319eb1f9b20c0d92c0"
#     }
#   }
# ])

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
#     'Accept': '*/*',
#     'Accept-Language': 'en-US,en;q=0.5',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Accept-Encoding': 'gzip, deflate, br',  # <- this tells server to compress, and requests auto-decompresses
#     'x-apollo-operation-name': 'GetBusinessReviewFeed',
#     'Content-Type': 'application/json',
#     'Cookie': cookies  # <- use the one loaded from file
# }

# response = requests.post(url, headers=headers, data=payload)

# # Make sure content is decompressed and parsed
# try:
#     json_data = response.json()
#     print(json.dumps(json_data, indent=2))
    
#         # Save to file
#     with open("reviews_yelp.json", "w", encoding="utf-8") as f:
#         json.dump(json_data, f, indent=2, ensure_ascii=False)
    
#     print(f"✅ {len(json_data)} reviews saved to reviews_yelp.json")
    
# except Exception:
#     print("Standard JSON parse failed, trying manual decoding...")
import json
from datetime import datetime

def extract_review_data(input_file, output_file):
    # Load the input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Initialize list to store extracted reviews
    extracted_reviews = []
    
    # Iterate through each review node
    for business_data in data:
        if 'data' in business_data and 'business' in business_data['data'] and 'reviews' in business_data['data']['business']:
            edges = business_data['data']['business']['reviews']['edges']
            
            for edge in edges:
                node = edge['node']
                
                # Safely handle bizUserPublicReply which might be None
                biz_reply = node.get('bizUserPublicReply')
                reply_text = biz_reply.get('text', '') if biz_reply else ''
                
                # Format dates
                try:
                    review_date = datetime.strptime(
                        node.get('createdAt', {}).get('localDateTimeForBusiness', ''),
                        '%Y-%m-%dT%H:%M:%S%z'
                    ).strftime('%Y-%m-%d')
                except (ValueError, AttributeError):
                    review_date = ''
                
                try:
                    reply_date = datetime.strptime(
                        biz_reply.get('createdAt', {}).get('localDateTimeForBusiness', ''),
                        '%Y-%m-%dT%H:%M:%S%z'
                    ).strftime('%Y-%m-%d') if biz_reply else ''
                except (ValueError, AttributeError):
                    reply_date = ''
                
                # Get LOVE_THIS reaction count
                love_this_count = 0
                reactions_container = node.get('availableReactionsContainer', {})
                if reactions_container and 'availableReactions' in reactions_container:
                    for reaction in reactions_container['availableReactions']:
                        if reaction.get('reactionType') == 'LOVE_THIS':
                            love_this_count = reaction.get('count', 0)
                            break
                
                # Extract basic review info
                review = {
                    'encid': node.get('encid', ''),
                    'text': node.get('text', {}).get('full', ''),
                    'rating': node.get('rating', 0),
                    'date_created': review_date,
                    'language': node.get('text', {}).get('language', ''),
                    'reviewer': {
                        'display_name': node.get('author', {}).get('displayName', ''),
                        'location': node.get('author', {}).get('displayLocation', ''),
                        'review_count': node.get('author', {}).get('reviewCount', 0)
                    },
                    'photos': [],
                    'business_reply': {
                        'text': reply_text,
                        'date': reply_date,
                        'owner': biz_reply.get('owner', {}).get('displayName', '') if biz_reply else ''
                    },
                    'love_this_count': love_this_count
                }
                
                # Extract photo information if available
                if 'businessPhotos' in node and node['businessPhotos']:
                    for photo in node['businessPhotos']:
                        photo_data = {
                            'url': photo.get('photoUrl', {}).get('url', ''),
                            'caption': photo.get('caption', ''),
                            'width': photo.get('width', 0),
                            'height': photo.get('height', 0)
                        }
                        review['photos'].append(photo_data)
                
                extracted_reviews.append(review)
    
    # Save the extracted data to a new JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_reviews, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully extracted {len(extracted_reviews)} reviews to {output_file}")

# Example usage
input_json = 'reviews_yelp.json'
output_json = 'extracted_reviews.json'
extract_review_data(input_json, output_json)