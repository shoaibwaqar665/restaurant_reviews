import json
from datetime import datetime
import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from myapp.dbOperations import InsertYelpReviewsBatch

def extract_review_yelp_data(input_file, output_file, business_key, location_id):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    try:
        edges = data["reviews"][0]["data"]["business"]["reviews"]["edges"]
    except (KeyError, IndexError, TypeError) as e:
        print(f"❌ Failed to find review edges: {e}")
        return

    extracted_reviews = []

    for edge in edges:
        node = edge.get("node", {})

        # Safely handle bizUserPublicReply
        biz_reply = node.get("bizUserPublicReply")
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
        reactions = node.get('availableReactionsContainer', {}).get('availableReactions', [])
        for reaction in reactions:
            if reaction.get('reactionType') == 'LOVE_THIS':
                love_this_count = reaction.get('count', 0)
                break

        # Extract review info
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

        # Extract photos if any
        for photo in node.get('businessPhotos', []):
            review['photos'].append({
                'url': photo.get('photoUrl', {}).get('url', ''),
                'caption': photo.get('caption', ''),
                'width': photo.get('width', 0),
                'height': photo.get('height', 0)
            })

        extracted_reviews.append(review)
        # InsertYelpReviewsBatch(review,'Burbank_1300 San Fernando_Burbank_CA_91504_shakeys_pizza_parlor', 'tuWl2S2O4YwI2qHXiIaSyw')


    # Save to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_reviews, f, indent=2, ensure_ascii=False)
    InsertYelpReviewsBatch(extracted_reviews,business_key, location_id)
    print(f"✅ Successfully extracted {len(extracted_reviews)} reviews to {output_file}")
    
