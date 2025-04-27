import asyncio
from bs4 import BeautifulSoup
import time
import nodriver as uc  # assuming you're using a wrapper around CDP
from urllib.parse import urlparse, parse_qs, unquote
import re
import requests
import zipfile
from nodriver import Config
import os

# from myapp.dbOperations import select_name_from_trip_business_details
# # def get_meta_content(soup, name):
# #     tag = soup.find("meta", attrs={"name": name})
# #     return tag["content"].strip() if tag and tag.get("content") else None

# # def get_directions_address(soup):
# #     tag = soup.find("p", class_="y-css-qn4gww")
# #     if tag and tag.find("a") and "Get Directions" in tag.text:
# #         return tag.text.strip()
# #     return None

# # def get_phone_number(soup):
# #     phone_tag = soup.find("p", string=lambda s: s and "Phone number" in s)
# #     if phone_tag:
# #         next_tag = phone_tag.find_next_sibling("p")
# #         if next_tag:
# #             return next_tag.text.strip()
# #     return None

# # def get_address(soup):
# #     phone_tag = soup.find("p", string=lambda s: s and "Get Directions" in s)
# #     if phone_tag:
# #         next_tag = phone_tag.find_next_sibling("p")
# #         if next_tag:
# #             raw_text = next_tag.text.replace("\n", "").strip()
# #             clean_address = re.sub(r'\s+', ' ', raw_text)
# #             return clean_address
# #     return None

# # def get_business_website(soup):
# #     p_tag = soup.find("p", class_="y-css-9fw56v", string="Business website")
# #     if p_tag:
# #         link = p_tag.find_next("a", href=True)
# #         if link:
# #             href = link["href"].strip()
# #             parsed_url = urlparse(href)
# #             query_params = parse_qs(parsed_url.query)
# #             return unquote(query_params["url"][0]) if "url" in query_params else href
# #     return None

# # def get_website_menu_link(soup):
# #     menu_divs = soup.find_all("div", class_="y-css-6az2m0")
# #     for div in menu_divs:
# #         if div.find("span", string="Website menu"):
# #             link_tag = div.find("a", href=True)
# #             if link_tag:
# #                 href = link_tag["href"].strip()
# #                 parsed_url = urlparse(href)
# #                 query_params = parse_qs(parsed_url.query)
# #                 return unquote(query_params["url"][0]) if "url" in query_params else href
# #     return None

# # def get_hours_of_operation(soup):
# #     hours_table = soup.find("table", class_="hours-table__09f24__KR8wh")
# #     hours = {}
# #     if hours_table:
# #         rows = hours_table.find_all("tr", class_="y-css-29kerx")
# #         for row in rows:
# #             day_tag = row.find("p", class_="day-of-the-week__09f24__JJea_")
# #             time_tag = row.find("p", class_="no-wrap__09f24__c3plq")
# #             if day_tag and time_tag:
# #                 hours[day_tag.get_text(strip=True)] = time_tag.get_text(strip=True)
# #     return hours

# # def get_custom_class_data(soup):
# #     elements = soup.find_all("div", class_="arrange-unit__09f24__rqHTg arrange-unit-fill__09f24__CUubG y-css-1n5biw7")
# #     for el in elements:
# #         text = el.get_text(separator=" ", strip=True)
# #         match = re.match(r"([\d.]+)\s+\((\d+)\s+reviews\)", text)
# #         if match:
# #             return {
# #                 "rating": float(match.group(1)),
# #                 "review_count": int(match.group(2))
# #             }
# #     return {"rating": None, "review_count": None}

# # def get_vibe_check_attributes(soup):
# #     vibe_section = soup.find("div", class_="y-css-gdh503", attrs={"data-testid": "VibeCheckAttributes"})
# #     vibe_attributes = []
# #     if vibe_section:
# #         vibe_items = vibe_section.find_all("div", class_="arrange__09f24__LDfbs")
# #         for item in vibe_items:
# #             label_tag = item.find("span", class_="y-css-1541nhh")
# #             if label_tag:
# #                 vibe_attributes.append(label_tag.text.strip())
# #     return vibe_attributes

# # def get_amenities(soup):
# #     amenities = []
# #     section = soup.find("section", {"aria-label": "Amenities and More"})
# #     if section:
# #         for item in section.select("div.arrange__09f24__LDfbs.vertical-align-baseline__09f24__fA6Jk"):
# #             label = item.select_one("span.y-css-qn4gww")
# #             value = item.select_one("span.label-spacing-v2__09f24__RiEXv")
# #             if label:
# #                 amenities.append(f"{label.text.strip()}: {value.text.strip()}" if value else label.text.strip())
# #     vibe_attrs = get_vibe_check_attributes(soup)
# #     for item in vibe_attrs:
# #         if item not in amenities:
# #             amenities.append(item)
# #     return amenities

# # def parse_yelp_html(data):
# #     # with open(input_file, "r", encoding="utf-8") as f:
# #     soup = BeautifulSoup(data, "html.parser")

# #     return {
# #         "meta_description": get_meta_content(soup, "description"),
# #         "yelp_biz_id": get_meta_content(soup, "yelp-biz-id"),
# #         "directions_address": get_directions_address(soup),
# #         "phone_number": get_phone_number(soup),
# #         "business_website": get_business_website(soup),
# #         "address": get_address(soup),
# #         "website_menu": get_website_menu_link(soup),
# #         "hours_of_operation": get_hours_of_operation(soup),
# #         "amenities": get_amenities(soup),
# #         "custom_class_data": get_custom_class_data(soup)
# #     }
# # geo.iproyal.com:12321:jxuQHPGrydd0jIva:RU7veaFCDR0nRHbL
# proxy = {
#     'server': 'geo.iproyal.com:12321',  
#     'username': 'jxuQHPGrydd0jIva',                
#     'password': 'RU7veaFCDR0nRHbL'
# }

# # Function to create a proxy plugin
# def createProxyPlugin(proxy):
#     PROXY_HOST, PROXY_PORT = proxy['server'].split(':')
#     PROXY_USER = proxy['username']
#     PROXY_PASS = proxy['password']
#     PROTOCOL = "http"  # Change as per your proxy's protocol

#     manifest_json = """
#     {
#         "version": "1.0.0",
#         "manifest_version": 2,
#         "name": "Chrome Proxy",
#         "permissions": [
#             "proxy",
#             "tabs",
#             "unlimitedStorage",
#             "storage",
#             "<all_urls>",
#             "webRequest",
#             "webRequestBlocking"
#         ],
#         "background": {
#             "scripts": ["background.js"]
#         },
#         "minimum_chrome_version":"22.0.0"
#     }
#     """

#     background_js = f"""
#     var config = {{
#         mode: "fixed_servers",
#         rules: {{
#             singleProxy: {{
#                 scheme: "{PROTOCOL}",
#                 host: "{PROXY_HOST}",
#                 port: parseInt({PROXY_PORT})
#             }},
#             bypassList: ["localhost"]
#         }}
#     }};
#     chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
#     function callbackFn(details) {{
#         return {{
#             authCredentials: {{
#                 username: "{PROXY_USER}",
#                 password: "{PROXY_PASS}"
#             }}
#         }};
#     }}
#     chrome.webRequest.onAuthRequired.addListener(
#         callbackFn,
#         {{urls: ["<all_urls>"]}},
#         ['blocking']
#     );
#     """

#     plugin_file = 'proxy_auth_plugin.zip'
#     with zipfile.ZipFile(plugin_file, 'w') as zp:
#         zp.writestr("manifest.json", manifest_json)
#         zp.writestr("background.js", background_js)
#     return plugin_file

# # Function to configure NoDriver with the new proxy
# def getConfigWithProxy():
#     plugin_file = createProxyPlugin(proxy)
#     config = Config()
#     config.add_extension(os.path.join(os.getcwd(), plugin_file))
#     return config


# def get_public_ip():
#     try:
#         # Send a GET request to ifconfig.me
#         response = requests.get("https://ifconfig.me")
        
#         # Check if the request was successful
#         if response.status_code == 200:
#             return response.text.strip()
#         else:
#             return "Failed to retrieve IP address"
#     except requests.exceptions.RequestException as e:
#         return f"An error occurred: {e}"

async def main():
    # config = getConfigWithProxy()
    browser = await uc.start()
    page = await browser.get('https://www.yelp.com/search?find_desc=shakey%27s+pizza+parlor&find_loc=5105+Torrance+Blvd%2C+Torrance%2C+90503')
    # ip_address = get_public_ip()
    # print(f"Your public IP address is: {ip_address}")
    time.sleep(20)
    cookies_data = await browser.cookies.get_all(requests_cookie_format=True)
    cookie_str = ''
    for cookies_mina in cookies_data:
        cookie_str += f"{cookies_mina.name}={cookies_mina.value}; "
    # Remove the trailing '; ' at the end
    cookie_str = cookie_str.strip()
    print(f"Cookies: {cookie_str}")
    time.sleep(10)
    # page_content = await page.get_content()

    # cleaned_data = parse_yelp_html(page_content)
    # print(cleaned_data)

asyncio.run(main())

# # import base64
# # s = "WzovFIQUtHDbSquR7VBdJlNMA0D52mNo-Dtn1NQJgwQ"
# # print(base64.urlsafe_b64decode(s + '==').decode())
# from dotenv import load_dotenv
# import os

# # Load environment variables from .env file
# load_dotenv()

# Scraping = {
#     "Database": os.getenv("DB_DATABASE"),
#     "Username": os.getenv("DB_USERNAME"),
#     "Password": os.getenv("DB_PASSWORD"),
#     "Host": os.getenv("DB_HOST"),
#     "Port": os.getenv("DB_PORT")
# }
# print(Scraping)
# datat= select_name_from_trip_business_details("shakey's pizza parlor")
# # datta= select_name_from_trip_business_details("shakeys pizza parlor")

# print(datat)
# # print(datta)

def slugify(query):
    query = query.lower()
    res_slug = ""

    for i, char in enumerate(query):
        if char == "'":
            if i == len(query) - 1:
                continue

            prev_char = query[i - 1] if i > 0 else ''
            next_char = query[i + 1] if i + 1 < len(query) else ''

            # Remove apostrophe if it's part of a possessive like "shakey's"
            if next_char == 's' and (i + 2 == len(query) or not query[i + 2].isalpha()):
                continue

            # Otherwise, replace with a hyphen
            res_slug += "-"
        else:
            res_slug += char

    res_slug = res_slug.replace(" ", "-")
    return res_slug

print(slugify("shakey's pizza parlor"))
