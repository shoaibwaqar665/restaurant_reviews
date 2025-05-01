
# from googlesearch import search
# from urllib.parse import urlparse, unquote
# from googlesearch import search



# def get_unique_yelp_urls(query, num_results=10):
#     urls = list(search(query, num_results=num_results))
#     yelp_urls = set()

#     for url in urls:
#         if "yelp.com/biz/" in url:
#             parsed = urlparse(url)
#             # Normalize domain (remove www.) and decode path
#             domain = parsed.netloc.replace("www.", "").replace("m.", "")
#             decoded_path = unquote(parsed.path)
#             clean_url = f"{parsed.scheme}://{domain}{decoded_path}"
#             yelp_urls.add(clean_url)

#     return list(yelp_urls)

# # Example usage
# data = get_unique_yelp_urls("yelp ovolo hong kong")
# for url in data:
#     print(url)
# print(get_unique_yelp_urls("yelp shakey's pizza los angeles"))
# print(get_longest_url("yelp ovolo hong kong"))


# from googlesearch import search

# def search_query(query, num_results=10):
#     return list(search(query, num_results=num_results))

# # Example
# for url in search_query("yelp ovolo hong kong"):
#     print(url)


# from myapp.dbOperations import select_name_from_trip_business_details


# data = select_name_from_trip_business_details("shakey's pizza parlor")
# print(data)

import re

result = "https://www.yelp.com/biz/shakeys-pizza-parlor-pico-rivera-2"
# Remove protocol and domain
slug_path = re.sub(r"^https?://(www\.)?yelp\.com/", "", result)
# Replace remaining slashes with dashes
restaurant_slug = slug_path.replace("/", "-")
print(restaurant_slug)
