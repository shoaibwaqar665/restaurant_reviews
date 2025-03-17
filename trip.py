from patchright.sync_api import sync_playwright
import time
import json
from datetime import datetime
import requests
# def save_cookies(cookies, filename):
#     # Save cookies in JSON format
#     with open(filename, 'w') as f:
#         json.dump(cookies, f, indent=4)
    
#     # Save cookies in raw string format
#     raw_cookies = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
#     with open('cookies.txt', 'w') as f:
#         f.write(raw_cookies)

# def run():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         page = browser.new_page()
        
#         try:
#             # Navigate to the page
#             page.goto("https://www.tripadvisor.com/Restaurant_Review-g32655-d534021-Reviews-Shakey_s_Pizza_Parlor-Los_Angeles_California.html")
            
#             # Wait for page to load
#             time.sleep(7)
            
#             # Get and save cookies
#             cookies = page.context.cookies()
#             cookie_filename = 'cookies_.json'
#             save_cookies(cookies, cookie_filename)
            
#             # Print page title
#             print(page.title())
            
#         except Exception as e:
#             print(f"An error occurred: {str(e)}")
#             raise
#         finally:
#             browser.close()

# if __name__ == "__main__":
#     run()

def parse_cookies(cookie_string):
    cookie_dict = {}
    for cookie in cookie_string.split('; '):
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            cookie_dict[name] = value
    return cookie_dict

# read cookies from cookies.txt
with open('cookies.txt', 'r') as f:
    cookie_string = f.read()

# Parse cookies into dictionary
cookies = parse_cookies(cookie_string)

# hit request to the url
url = "https://www.tripadvisor.com/Restaurant_Review-g32655-d534021-Reviews-Shakey_s_Pizza_Parlor-Los_Angeles_California.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(url, cookies=cookies, headers=headers)

# save the response to a file
with open('response.html', 'w') as f:
    f.write(response.text)
