# import asyncio
# from bs4 import BeautifulSoup
# import time
# import nodriver as uc  # assuming you're using a wrapper around CDP
# from urllib.parse import urlparse, parse_qs, unquote
# import re
# import requests
# import zipfile
# import os
# import urllib.parse

# from myapp.google_reviews import upload_to_s3

# from nodriver import Config
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

# async def main():
#     config = getConfigWithProxy()

#     browser = await uc.start(config=config)
#     # restaurant_name = "shakey's pizza parlor"
#     page = await browser.get(f'https://whatismyipaddress.com/')

#     time.sleep(10)
#     screenshot_path = "end.png"
#     await page.save_screenshot(screenshot_path)
#     url = upload_to_s3(screenshot_path, 's3teaconnect')
#     if url:
#         print(f"Presigned URL for screenshot: {url}")

#     browser.stop()
#     # soup = BeautifulSoup(html_content, "html.parser")
#     # extract_ip_addresses(html_content)

# # Step 2: Find the specific <section class="bit_more_info">
#     # bit_more_info_section = soup.find("section", class_="bit_more_info")

#     # if bit_more_info_section:
#     #     # Step 3: Extract hostname and useragent from inside that section
#     #     hostname_element = bit_more_info_section.find("span", id="hostname")
#     #     useragent_element = bit_more_info_section.find("span", id="useragent")

#     #     hostname = hostname_element.text.strip() if hostname_element else None
#     #     user_agent = useragent_element.text.strip() if useragent_element else None

#     #     # Step 4: Save into the class
#     #     bit_more_info = BitMoreInfo(hostname=hostname, user_agent=user_agent)
#     #     print(bit_more_info)
    
# asyncio.run(main())

# # # # import base64
# # # # s = "WzovFIQUtHDbSquR7VBdJlNMA0D52mNo-Dtn1NQJgwQ"
# # # # print(base64.urlsafe_b64decode(s + '==').decode())
# # # from dotenv import load_dotenv
# # # import os

# # # # Load environment variables from .env file
# # # load_dotenv()

# # # Scraping = {
# # #     "Database": os.getenv("DB_DATABASE"),
# # #     "Username": os.getenv("DB_USERNAME"),
# # #     "Password": os.getenv("DB_PASSWORD"),
# # #     "Host": os.getenv("DB_HOST"),
# # #     "Port": os.getenv("DB_PORT")
# # # }
# # # print(Scraping)
# # # datat= select_name_from_trip_business_details("shakey's pizza parlor")
# # # # datta= select_name_from_trip_business_details("shakeys pizza parlor")

# # # print(datat)
# # # # print(datta)

# # def slugify(query):
# #     query = query.lower()
# #     res_slug = ""

# #     for i, char in enumerate(query):
# #         if char == "'":
# #             if i == len(query) - 1:
# #                 continue

# #             prev_char = query[i - 1] if i > 0 else ''
# #             next_char = query[i + 1] if i + 1 < len(query) else ''

# #             # Remove apostrophe if it's part of a possessive like "shakey's"
# #             if next_char == 's' and (i + 2 == len(query) or not query[i + 2].isalpha()):
# #                 continue

# #             # Otherwise, replace with a hyphen
# #             res_slug += "-"
# #         else:
# #             res_slug += char

# #     res_slug = res_slug.replace(" ", "-")
# #     return res_slug

# # print(slugify("shakey's pizza parlor"))

# # from bs4 import BeautifulSoup

# # def find_unique_restaurants(file_path, restaurant_name):
# #     # Read the HTML content from file
# #     with open(file_path, 'r', encoding='utf-8') as file:
# #         html_content = file.read()
    
# #     normalized_name = normalize_text(restaurant_name)
# #     soup = BeautifulSoup(html_content, "html.parser")
    
# #     seen = set()
# #     unique_results = []
    
# #     for div in soup.find_all('div', class_="y-css-mhg9c5"):
# #         a_tag = div.find('a', attrs={"name": True})
# #         if a_tag:
# #             a_name = normalize_text(urllib.parse.unquote(a_tag['name']))
# #             if normalized_name in a_name:
# #                 name = a_tag.get_text(strip=True)
# #                 link = a_tag['href']
# #                 key = (name, link)
# #                 if key not in seen:
# #                     seen.add(key)
# #                     unique_results.append({
# #                         # "name": name,
# #                         "link": link
# #                     })
    
# #     return unique_results

# # # Example usage
# # file_path = "yelp_anaheim.txt"  # <-- Replace with your actual HTML file path
# # # restaurant_name = "shakey's pizza parlor"
# # restaurant_name = "shakey’s pizza parlor"
# # matches = find_unique_restaurants(file_path, restaurant_name)

# # if matches:
# #     for match in matches:
# #         print("Restaurant Info Found:", match['link'])
# # else:
# #     print("No restaurant found.")

from patchright.sync_api import sync_playwright
import time

from myapp.google_reviews import upload_to_s3
def main():
    with sync_playwright() as p:
        # Proxy settings
        proxy_settings = {
            "server": "http://geo.iproyal.com:12321",
            "username": "jxuQHPGrydd0jIva",
            "password": "RU7veaFCDR0nRHbL"
        }

        # Launch browser with proxy
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        print("Browser launched.")

        # Go to Google Search
        search_url = 'https://www.google.com/search?q=Shakey%27s+Pizza+Parlor+10340+Reseda+Blvd+Northridge%2C+CA+91326+yelp'
        page.goto(search_url)
        print("Navigated to Google search.")
        page.wait_for_load_state('networkidle')

        # Accept cookies if needed
        # Screenshot
        screenshot_path = "end.png"
        page.screenshot(path=screenshot_path)
        print("Screenshot taken.")

        # Upload to S3
        url = upload_to_s3(screenshot_path, 's3teaconnect')
        if url:
            print(f"Presigned URL for screenshot: {url}")
        try:
            page.locator("button:has-text('Accept all')").click(timeout=3000)
        except:
            pass  # Ignore if not found

        # Click on the first result
        page.locator("h3").first.click()
        print("Clicked first result.")
        page.wait_for_load_state('networkidle')
        time.sleep(5)  # Wait in case additional content is still loading

        # Screenshot
        screenshot_path = "end.png"
        page.screenshot(path=screenshot_path)
        print("Screenshot taken.")

        # Upload to S3
        url = upload_to_s3(screenshot_path, 's3teaconnect')
        if url:
            print(f"Presigned URL for screenshot: {url}")
        print("Review capture completed.")

        browser.close()

if __name__ == "__main__":
    main()