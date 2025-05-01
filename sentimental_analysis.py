# # # # import asyncio
# # # # from bs4 import BeautifulSoup
# # # # import time
# # # # import nodriver as uc  # assuming you're using a wrapper around CDP
# # # # from urllib.parse import urlparse, parse_qs, unquote
# # # # import re
# # # # import requests
# # # # import zipfile
# # # # import os
# # # # import urllib.parse

# # # # from myapp.google_reviews import upload_to_s3

# # # # from nodriver import Config
# # # # proxy = {
# # # #     'server': 'geo.iproyal.com:12321',  
# # # #     'username': 'jxuQHPGrydd0jIva',                
# # # #     'password': 'RU7veaFCDR0nRHbL'
# # # # }

# # # # # Function to create a proxy plugin
# # # # def createProxyPlugin(proxy):
# # # #     PROXY_HOST, PROXY_PORT = proxy['server'].split(':')
# # # #     PROXY_USER = proxy['username']
# # # #     PROXY_PASS = proxy['password']
# # # #     PROTOCOL = "http"  # Change as per your proxy's protocol

# # # #     manifest_json = """
# # # #     {
# # # #         "version": "1.0.0",
# # # #         "manifest_version": 2,
# # # #         "name": "Chrome Proxy",
# # # #         "permissions": [
# # # #             "proxy",
# # # #             "tabs",
# # # #             "unlimitedStorage",
# # # #             "storage",
# # # #             "<all_urls>",
# # # #             "webRequest",
# # # #             "webRequestBlocking"
# # # #         ],
# # # #         "background": {
# # # #             "scripts": ["background.js"]
# # # #         },
# # # #         "minimum_chrome_version":"22.0.0"
# # # #     }
# # # #     """

# # # #     background_js = f"""
# # # #     var config = {{
# # # #         mode: "fixed_servers",
# # # #         rules: {{
# # # #             singleProxy: {{
# # # #                 scheme: "{PROTOCOL}",
# # # #                 host: "{PROXY_HOST}",
# # # #                 port: parseInt({PROXY_PORT})
# # # #             }},
# # # #             bypassList: ["localhost"]
# # # #         }}
# # # #     }};
# # # #     chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
# # # #     function callbackFn(details) {{
# # # #         return {{
# # # #             authCredentials: {{
# # # #                 username: "{PROXY_USER}",
# # # #                 password: "{PROXY_PASS}"
# # # #             }}
# # # #         }};
# # # #     }}
# # # #     chrome.webRequest.onAuthRequired.addListener(
# # # #         callbackFn,
# # # #         {{urls: ["<all_urls>"]}},
# # # #         ['blocking']
# # # #     );
# # # #     """

# # # #     plugin_file = 'proxy_auth_plugin.zip'
# # # #     with zipfile.ZipFile(plugin_file, 'w') as zp:
# # # #         zp.writestr("manifest.json", manifest_json)
# # # #         zp.writestr("background.js", background_js)
# # # #     return plugin_file

# # # # # Function to configure NoDriver with the new proxy
# # # # def getConfigWithProxy():
# # # #     plugin_file = createProxyPlugin(proxy)
# # # #     config = Config()
# # # #     config.add_extension(os.path.join(os.getcwd(), plugin_file))
# # # #     return config

# # # # async def main():
# # # #     config = getConfigWithProxy()

# # # #     browser = await uc.start(config=config)
# # # #     # restaurant_name = "shakey's pizza parlor"
# # # #     page = await browser.get(f'https://whatismyipaddress.com/')

# # # #     time.sleep(10)
# # # #     screenshot_path = "end.png"
# # # #     await page.save_screenshot(screenshot_path)
# # # #     url = upload_to_s3(screenshot_path, 's3teaconnect')
# # # #     if url:
# # # #         print(f"Presigned URL for screenshot: {url}")

# # # #     browser.stop()
# # # #     # soup = BeautifulSoup(html_content, "html.parser")
# # # #     # extract_ip_addresses(html_content)

# # # # # Step 2: Find the specific <section class="bit_more_info">
# # # #     # bit_more_info_section = soup.find("section", class_="bit_more_info")

# # # #     # if bit_more_info_section:
# # # #     #     # Step 3: Extract hostname and useragent from inside that section
# # # #     #     hostname_element = bit_more_info_section.find("span", id="hostname")
# # # #     #     useragent_element = bit_more_info_section.find("span", id="useragent")

# # # #     #     hostname = hostname_element.text.strip() if hostname_element else None
# # # #     #     user_agent = useragent_element.text.strip() if useragent_element else None

# # # #     #     # Step 4: Save into the class
# # # #     #     bit_more_info = BitMoreInfo(hostname=hostname, user_agent=user_agent)
# # # #     #     print(bit_more_info)
    
# # # # asyncio.run(main())

# # # # # # # import base64
# # # # # # # s = "WzovFIQUtHDbSquR7VBdJlNMA0D52mNo-Dtn1NQJgwQ"
# # # # # # # print(base64.urlsafe_b64decode(s + '==').decode())
# # # # # # from dotenv import load_dotenv
# # # # # # import os

# # # # # # # Load environment variables from .env file
# # # # # # load_dotenv()

# # # # # # Scraping = {
# # # # # #     "Database": os.getenv("DB_DATABASE"),
# # # # # #     "Username": os.getenv("DB_USERNAME"),
# # # # # #     "Password": os.getenv("DB_PASSWORD"),
# # # # # #     "Host": os.getenv("DB_HOST"),
# # # # # #     "Port": os.getenv("DB_PORT")
# # # # # # }
# # # # # # print(Scraping)
# # # # # # datat= select_name_from_trip_business_details("shakey's pizza parlor")
# # # # # # # datta= select_name_from_trip_business_details("shakeys pizza parlor")

# # # # # # print(datat)
# # # # # # # print(datta)

# # # # # def slugify(query):
# # # # #     query = query.lower()
# # # # #     res_slug = ""

# # # # #     for i, char in enumerate(query):
# # # # #         if char == "'":
# # # # #             if i == len(query) - 1:
# # # # #                 continue

# # # # #             prev_char = query[i - 1] if i > 0 else ''
# # # # #             next_char = query[i + 1] if i + 1 < len(query) else ''

# # # # #             # Remove apostrophe if it's part of a possessive like "shakey's"
# # # # #             if next_char == 's' and (i + 2 == len(query) or not query[i + 2].isalpha()):
# # # # #                 continue

# # # # #             # Otherwise, replace with a hyphen
# # # # #             res_slug += "-"
# # # # #         else:
# # # # #             res_slug += char

# # # # #     res_slug = res_slug.replace(" ", "-")
# # # # #     return res_slug

# # # # # print(slugify("shakey's pizza parlor"))

# # # # # from bs4 import BeautifulSoup

# # # # # def find_unique_restaurants(file_path, restaurant_name):
# # # # #     # Read the HTML content from file
# # # # #     with open(file_path, 'r', encoding='utf-8') as file:
# # # # #         html_content = file.read()
    
# # # # #     normalized_name = normalize_text(restaurant_name)
# # # # #     soup = BeautifulSoup(html_content, "html.parser")
    
# # # # #     seen = set()
# # # # #     unique_results = []
    
# # # # #     for div in soup.find_all('div', class_="y-css-mhg9c5"):
# # # # #         a_tag = div.find('a', attrs={"name": True})
# # # # #         if a_tag:
# # # # #             a_name = normalize_text(urllib.parse.unquote(a_tag['name']))
# # # # #             if normalized_name in a_name:
# # # # #                 name = a_tag.get_text(strip=True)
# # # # #                 link = a_tag['href']
# # # # #                 key = (name, link)
# # # # #                 if key not in seen:
# # # # #                     seen.add(key)
# # # # #                     unique_results.append({
# # # # #                         # "name": name,
# # # # #                         "link": link
# # # # #                     })
    
# # # # #     return unique_results

# # # # # # Example usage
# # # # # file_path = "yelp_anaheim.txt"  # <-- Replace with your actual HTML file path
# # # # # # restaurant_name = "shakey's pizza parlor"
# # # # # restaurant_name = "shakey’s pizza parlor"
# # # # # matches = find_unique_restaurants(file_path, restaurant_name)

# # # # # if matches:
# # # # #     for match in matches:
# # # # #         print("Restaurant Info Found:", match['link'])
# # # # # else:
# # # # #     print("No restaurant found.")

# # # # from patchright.sync_api import sync_playwright
# # # from patchright.sync_api import sync_playwright
# # # import time

# # # from myapp.google_reviews import upload_to_s3
# # # def main():
# # #     with sync_playwright() as p:
# # #         # Proxy settings
# # #         proxy_settings = {
# # #             "server": "http://geo.iproyal.com:12321",
# # #             "username": "jxuQHPGrydd0jIva",
# # #             "password": "RU7veaFCDR0nRHbL"
# # #         }

# # #         # Launch browser with proxy
# # #         browser = p.chromium.launch(headless=False, proxy=proxy_settings)
# # #         context = browser.new_context(viewport={'width': 1280, 'height': 800})
# # #         page = context.new_page()
# # #         print("Browser launched.")

# # #         # Go to Google Search
# # #         search_url = 'https://www.google.com/search?q=Shakey%27s+Pizza+Parlor+10340+Reseda+Blvd+Northridge%2C+CA+91326+yelp'
# # #         page.goto(search_url)
# # #         print("Navigated to Google search.")
# # #         page.wait_for_load_state('networkidle')

# # #         # Accept cookies if needed
# # #         # Screenshot
# # #         screenshot_path = "end.png"
# # #         page.screenshot(path=screenshot_path)
# # #         print("Screenshot taken.")

# # #         # Upload to S3
# # #         url = upload_to_s3(screenshot_path, 's3teaconnect')
# # #         if url:
# # #             print(f"Presigned URL for screenshot: {url}")
# # #         try:
# # #             page.locator("button:has-text('Accept all')").click(timeout=3000)
# # #         except:
# # #             pass  # Ignore if not found

# # #         # Click on the first result
# # #         page.locator("h3").first.click()
# # #         print("Clicked first result.")
# # #         page.wait_for_load_state('networkidle')
# # #         time.sleep(5)  # Wait in case additional content is still loading

# # #         # Screenshot
# # #         screenshot_path = "end.png"
# # #         page.screenshot(path=screenshot_path)
# # #         print("Screenshot taken.")

# # #         # Upload to S3
# # #         url = upload_to_s3(screenshot_path, 's3teaconnect')
# # #         if url:
# # #             print(f"Presigned URL for screenshot: {url}")
# # #         print("Review capture completed.")

# # #         browser.close()

# # # if __name__ == "__main__":
# # #     main()

# # # import subprocess


# # # def execute_bash_script(restaurant_slug):
# # #     # Define the bash script file path
# # #     bash_script = 'myapp/run_curl.sh'

# # #     # Run the bash script with the restaurant_slug argument
# # #     result = subprocess.run([bash_script, restaurant_slug], capture_output=True, text=True)

# # #     # Print the output and error (if any)
# # #     if result.returncode == 0:
# # #         print("Script executed successfully!")
# # #         print("Output:", result.stdout)
# # #     else:
# # #         print("Error executing the script.")
# # #         print("Error:", result.stderr)


# # # execute_bash_script("shakeys-pizza-parlor-northridge-4")

# # # def execute_bash_loc_script(query,location):
# # #     # Define the bash script file path
# # #     bash_script = 'myapp/loc_curl.sh'

# # #     # Run the bash script with the restaurant_slug argument
# # #     result = subprocess.run([bash_script, query,location], capture_output=True, text=True)

# # #     # Print the output and error (if any)
# # #     if result.returncode == 0:
# # #         print("Script executed successfully!")
# # #         print("Output:", result.stdout)
# # #     else:
# # #         print("Error executing the script.")
# # #         print("Error:", result.stderr)
# # #     # Define the bash script file path
    
# # # execute_bash_loc_script("shakeys pizza parlor","10340 Reseda Blvd Northridge, CA 91326")

# # import requests

# # url = "https://www.google.com/search?q=Shakey%27s+Pizza+Parlor+1027+S+Harbor+Blvd+Anaheim+92805+yelp"

# # payload = {}
# # headers = {
# #   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
# #   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
# #   'Accept-Language': 'en-US,en;q=0.5',
# #   'Accept-Encoding': 'gzip, deflate, br, zstd',
# #   'Alt-Used': 'www.google.com',
# #   'Connection': 'keep-alive',
# #   'Cookie': 'AEC=AVcja2dv4_9OTjlSWU1VqxxpieF7WSDkdbcyKj5gvtIHEp1XztD3WlUz9A; NID=523=BcvWxC-sJUvs2dnF7mByuRF0_r0UWprEJ-jm9NlHTxiOnfG8AkPuIXFzUFwbnVRVkiWah-JczRfq5s2LPmYT2Ak3_sV7nf5vn_a9Ux6gGwkJFg04DCiKr-citVp0gJwqiM3gJAnaX0C9WrmaH8R0pZPOn98Qbk9UyOaP2lH9cXnjeq8OqihO9D0RTaj2rS9PggCzHcD_v6z96djKDBjWJT0zdBfX5CA-qp3YnpaCm9kiML5_nXRUI8MRdLY_7WW0KFT3PBhGKoP-Af2NnQyxYca4A_HwGegKVwsBHuuTeM5uVciHYs0ZDdBKzWmtS_L-Bnc_EsT0hl6daQD6BoQQ6evkSDWxhD7TLWfSVRIadKDw2qDUxEyTM157J7iCzH5jvWscEXrSpSlRrYG6uuQvZ4tuUTSDQoC2-qZKAq4XwVFKeRBkRpJOM14POucu1sSW6Obcq1yxEt5SuTIXZAZIh52GzLX-DKB8W68BEMs79tbBnSmsKK0K7b9VWI65sEFIniWnfq5qQ2q31m2oHhpNy6rY5SDrj_yuPjkYhYC6jQu025trSLFAg6h1QMrjchR_JhbHO6hUgmQLd73dKJ8wxoRUDMMvFMXPs_KLf4p3Flc__gutKrk5Rh8kWN4LKwtot34w9RMCcenUKqQuVEn7KAZtOYdN8LYSw1I5YqIn_uJ2kw4gtnj7_mknK1jef1A0dol7cuBEFqqq3yo7b1LMXZHpI0ClgwaN5dp8Zo7OUtU4ssACG7fTz9U; SID=g.a000vghLBsgkrjBcuw6oih6-pxAhP9NRRxCFt0tz23gJ7F2nzsvJw_mQaWVUe86CQeVONVXd7QACgYKARISARISFQHGX2MiHSfyxVS4pyog1DJWRGLDcRoVAUF8yKp6MgplIII0xpzMXLDOGyv60076; __Secure-1PSID=g.a000vghLBsgkrjBcuw6oih6-pxAhP9NRRxCFt0tz23gJ7F2nzsvJcbDAOWigAEch3lDLqWV-WgACgYKARoSARISFQHGX2MiEXQMubJ51zv-bU5nDkyjKhoVAUF8yKo5BvGJjyBkw2T7K8j_FyL80076; __Secure-3PSID=g.a000vghLBsgkrjBcuw6oih6-pxAhP9NRRxCFt0tz23gJ7F2nzsvJiOcxWMDZoLnGc_zr1LdtVwACgYKAdsSARISFQHGX2Misd34UJbAgIZ6So9lF5v2lhoVAUF8yKoVCR3Fi1aGenbfWiuZkxdR0076; HSID=AXxOHY_B6ktrhE9-L; SSID=AjJYFuM68L1jD_XGo; APISID=ZargMzlWmR4jzifG/ATCt66Mzukyr01NqC; SAPISID=_I7HJoaUfcRpAjls/A6jRTiKXOH-LJU3kz; __Secure-1PAPISID=_I7HJoaUfcRpAjls/A6jRTiKXOH-LJU3kz; __Secure-3PAPISID=_I7HJoaUfcRpAjls/A6jRTiKXOH-LJU3kz; SIDCC=AKEyXzUPbSbPy8pkxzkua4M7YA4f4nf74c0q6_lRaF5QnvroN4mv8jtqpFWqHV3cPmR7hVYQtoEa; __Secure-1PSIDCC=AKEyXzUxJA2SRjgbJbh3ZEKO-2gv24QsXWfYtliFZdF62GKmD9KasmKrgBfB1kgmTatu7C2O4GUo; __Secure-3PSIDCC=AKEyXzUZcwRCQ_CrrJIxuWqHJPse4B_bRandmuwQrXrLagrKVYrKHca71nRYvHefbMxjjt9pm2Y; SEARCH_SAMESITE=CgQI2p0B; __Secure-1PSIDTS=sidts-CjIBjplskN_xyoD39m45mdwe_9D3d-R3fmB3FnqN992EV0dhU2WQsjpcVQ0NE2nqQjeQfBAA; __Secure-3PSIDTS=sidts-CjIBjplskN_xyoD39m45mdwe_9D3d-R3fmB3FnqN992EV0dhU2WQsjpcVQ0NE2nqQjeQfBAA; __Secure-ENID=27.SE=nOrN9OIyxFuspw6I4NncPm9ZKMo6fV7BAxluKEStPHwNOAcA6J6BuzZFs1vsY0qCytRxOz0ruPLJ-bdKtPwvMRM9AUkDlkZRG-gr6n7vaDedlLoP4sO9zI0OIxUIRIpIBRlcrhZbrGagezhmlAh3dUBXU87tdFs_5K8j1fa06dH_GLTxtwxggEILfLIfmytfbSwYFO5RQl14MuLl0gopM4VbcFV9Msx4jjuzFPxRQWFGz_8oCVyDKGzZ4j6YDcaSJ-ImY9Y5dCZys9Gdz8DCKkZYz3-_TfRD6OcFzwBgYdiA14zBZkx2rJSjntS1TK8ZxY12MAu50maKgHrmITQK73kzcCg5U6WBseat5w; OTZ=8030630_36_36__36_; OGPC=19036484-1:; DV=g_tDITdZfYxrELt8hEqnbj2ypByHaJlw4P5MyRCtgwAAAKDFqKjTvhxqVwAAACiFq6AsToMGGAAAACDi14a58OXZDwAAwE_ZUzZiriibBAAAAA',
# #   'Upgrade-Insecure-Requests': '1',
# #   'Sec-Fetch-Dest': 'document',
# #   'Sec-Fetch-Mode': 'navigate',
# #   'Sec-Fetch-Site': 'none',
# #   'Sec-Fetch-User': '?1',
# #   'Priority': 'u=0, i',
# #   'TE': 'trailers'
# # }

# # response = requests.request("GET", url, headers=headers, data=payload)

# # # write the response to a file
# # with open("response.html", "w") as file:
# #     file.write(response.text)
# # # print(response.text)


# import requests

# url = "https://links.duckduckgo.com/d.js?q=https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dyelp%2BShakey%2527s%2BPizza%2BParlor&t=E&l=us-en&s=0&a=ffab&dl=en&ct=PK&vqd=4-100454408292883811920879363727046880627&bing_market=en-US&gjs=urldecode&p_ent=&ex=-1&dp=Fii__kknIpwp6gyiKFalzBAYYWKGhuzEKFo3YoDkmHoHsZTII1VgJ9j32KFryn-YOOBhMgaWTTKPJoOp6-9e3hB5B8zGd1PILxknwuYAwLtcYEEut6fArhFRLg59MXRDG55d84FwOJKd8VlxY1KvNuCSUBb7vYTdUiSVw-Ros_AO6CdoaRCmYGmsMWsD0_ybWUknixWcwZB52Rn8ttqm2JgXfon1vEb-omnbSgITjzE.ZmJ2NtmgLknroy50AoOaJw&perf_id=44b14fa0866adfb7&parent_perf_id=fb7f0734ebbd0b35&host_region=inc&dfrsp=1&wrap=1&aps=0&aboutmapsexp=b&biaexp=b&direxp=b&litexp=a&msvrtexp=b&newsexp=b&shoppingexp=b"

# payload = {}
# headers = {
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
#   'Accept': '*/*',
#   'Accept-Language': 'en-US,en;q=0.5',
#   'Accept-Encoding': 'gzip, deflate, br, zstd',
#   'Referer': 'https://duckduckgo.com/',
#   'Connection': 'keep-alive',
#   'Sec-Fetch-Dest': 'script',
#   'Sec-Fetch-Mode': 'no-cors',
#   'Sec-Fetch-Site': 'same-site',
#   'Priority': 'u=1'
# }

# response = requests.request("GET", url, headers=headers, data=payload)
# with open("response_.html", "w") as file:
#     file.write(response.text)
# print(response.text)
from googlesearch import search

# def search_query(query, num_results=2):
#     return list(search(query, num_results=num_results))

# # Example
# urls = search_query("yelp shakey's pizza parlor 3615 Pacific Coast Hwy Torrance, CA 90505")

# # Sort the URLs by their length
# sorted_urls = sorted(urls, key=len, reverse=True)

# # Print the sorted URLs
# # for url in sorted_urls:
# print(sorted_urls[0])

# from googlesearch import search

# def get_longest_url(query, num_results=2):
#     urls = list(search(query, num_results=num_results))
#     sorted_urls = sorted(urls, key=len, reverse=True)
#     return sorted_urls if sorted_urls else None

# result = get_longest_url("yelp shakey's pizza parlor 14300 Se Petrovitsky Rd, Renton, 8905")
# print(result)

# import requests

# def search_query(query):
#     response = requests.get(f'https://api.duckduckgo.com/?q={query}&format=json')
#     data = response.json()
#     links = [result['FirstURL'] for result in data.get('RelatedTopics', []) if 'FirstURL' in result]
#     return links

# # Example
# for link in search_query("yelp Shakey's Pizza Parlor 10340 Reseda Blvd Northridge CA 91326"):
#     print(link)

# restaurant_slug = result.replace("https://www.yelp.com/", "").replace("/", "-")
# print(restaurant_slug)
import re

def clean_address(address: str) -> str:
    # Pattern matches a 5-digit ZIP followed by a dash and more digits (e.g. 98058-8905)
    return re.sub(r'\b(\d{5})-\d{4}\b', r'\1', address)

# Test examples
addresses = "13701 Foothill Blvd, Los Angeles, 91342-3105"


print(clean_address(addresses))
