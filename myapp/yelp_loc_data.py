import json
import urllib.parse
from bs4 import BeautifulSoup
from myapp.dbOperations import fetch_yelp_data, select_name_from_trip_business_details
from myapp.google_reviews import upload_to_s3
from myapp.trip import FetchAndStoreRestaurantData
from myapp.yelp_location_clean import yelp_loc_clean
from concurrent.futures import ThreadPoolExecutor
from ninja_extra import api_controller, http_post, NinjaExtraAPI,http_get
yelp_api = NinjaExtraAPI(urls_namespace='Yelp')
from myapp.schema import Yelp
from typing import Dict
import os
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
import time
import nodriver as uc  
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests
import zipfile
from nodriver import Config
import os
proxy = {
    'server': 'geo.iproyal.com:12321',  
    'username': 'jxuQHPGrydd0jIva',                
    'password': 'RU7veaFCDR0nRHbL'
}

# Function to create a proxy plugin
def createProxyPlugin(proxy):
    PROXY_HOST, PROXY_PORT = proxy['server'].split(':')
    PROXY_USER = proxy['username']
    PROXY_PASS = proxy['password']
    PROTOCOL = "http"  # Change as per your proxy's protocol

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "{PROTOCOL}",
                host: "{PROXY_HOST}",
                port: parseInt({PROXY_PORT})
            }},
            bypassList: ["localhost"]
        }}
    }};
    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{PROXY_USER}",
                password: "{PROXY_PASS}"
            }}
        }};
    }}
    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
    """

    plugin_file = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_file

# Function to configure NoDriver with the new proxy
def getConfigWithProxy():
    plugin_file = createProxyPlugin(proxy)
    config = Config()
    config.add_extension(os.path.join(os.getcwd(), plugin_file))
    return config

# --------------------- nodriver ----------------------
def normalize_text(text):
    """Normalize text by replacing curly quotes and making lowercase."""
    if not text:
        return ""
    return text.replace('’', "'").lower().strip()

async def extract_location_links(query,address):
    print("Extracting location links")
    config = getConfigWithProxy()

    browser = await uc.start(config=config)
    print(f'query: {query}', f'address: {address}')
    # restaurant_name = "shakey's pizza parlor"
    page = await browser.get(f'https://www.yelp.com/search?find_desc={query}&find_loc={address}')
    print("browser navigated to yelp")
    time.sleep(15)
    screenshot_path = "end.png"
    await page.save_screenshot(screenshot_path)
    url = upload_to_s3(screenshot_path, 's3teaconnect')
    if url:
        print(f"Presigned URL for screenshot: {url}")

    html_content = await page.get_content()
    print(html_content)
    browser.stop()
    normalized_name = normalize_text(query)
    soup = BeautifulSoup(html_content, "html.parser")
    
    seen = set()
    unique_results = []
    
    for div in soup.find_all('div', class_="y-css-mhg9c5"):
        a_tag = div.find('a', attrs={"name": True})
        if a_tag:
            a_name = normalize_text(urllib.parse.unquote(a_tag['name']))
            if normalized_name in a_name:
                name = a_tag.get_text(strip=True)
                link = a_tag['href']
                key = (name, link)
                if key not in seen:
                    seen.add(key)
                    unique_results.append(
                        link
                    )
                    # print(link)
    return unique_results


async def extract_location_html(restaurant_slug):
    config = getConfigWithProxy()
    browser = await uc.start(config=config)
    url = f"https://www.yelp.com{restaurant_slug}"
    page = await browser.get(url)
    time.sleep(20)
    page_content = await page.get_content()
    cookies_data = await browser.cookies.get_all(requests_cookie_format=True)
    cookie_str = ''
    for cookies_mina in cookies_data:
        cookie_str += f"{cookies_mina.name}={cookies_mina.value}; "
    print(f"Cookies: {cookie_str}")
    with open("yelp_cookies.txt", "w") as f:
        f.write(cookie_str)
    browser.stop()
    return page_content
    # cleaned_data = parse_yelp_html(page_content)
# --------------------- nodriver ----------------------
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

# Pass the restaurant slug as an argument
# restaurant_slug = 'shakeys-pizza-parlor-burbank'
async def FetchYelpData(query):
    print('FetchYelpData')
    location_names = select_name_from_trip_business_details(query)
    if len(location_names) == 0:
        print("No restaurant name found")
        data_flag = FetchAndStoreRestaurantData(query)
        if data_flag:
            print('data_flag is true')
            location_names = select_name_from_trip_business_details(query)
            print('restaurant names',location_names)
    else:
        print("Restaurant names found")
    print(f"Location names: {location_names}")
    res_slug = slugify(query)
    for location in location_names:
        try:
            restaurant_slug = res_slug + "-" + location.replace(" ", "-").lower()
            restaurant_slug = restaurant_slug.replace(" ", "-")
            

            print(f"🚀 Executing script for restaurant slug: {restaurant_slug}")
            unique_results = await extract_location_links(query,location)
            for result in unique_results:
                print('Navigating to:',result)
                html_content = await extract_location_html(result)

                # input_file = input_file = os.path.join(base_dir, restaurant_slug + ".html")
                output_file = restaurant_slug + ".json"

                yelp_loc_clean(html_content, output_file, query, location)

        # except FileNotFoundError as e:
        #     print(f"❌ File not found for location '{location}': {e}")
        except ValueError as ve:
            print(f"⚠️ Value error for location '{location}': {ve}")
        except Exception as e:
            print(f"❌ Unexpected error occurred for location '{location}': {e}")

def run_async_main(query):
    return asyncio.run(FetchYelpData(query))


def forward_to_yelp(query):
    time.sleep(3)
    # url = "http://44.202.182.5:8000/yelp/next_restaurant_details"
    url = "http://3.92.196.22:8000/yelp/next_restaurant_details"
    # url = "http://127.0.0.1:8000/yelp/next_restaurant_details"
    print("URL:", url)

    payload = json.dumps({
      "query": query
    })
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

@api_controller("", tags=["Yelp"])
class YelpController:
    
    
    @http_post('/next_restaurant_details', response={200: Dict, 400: Dict})
    async def next_restaurant_details_for_yelp(self,request, data: Yelp):
        """Return restaurant details for a specific ID"""
        try:
           query = data.query
           print(query)
        #    executor = ThreadPoolExecutor()
        #    future = executor.submit(FetchYelpData,query )
           loop = asyncio.get_event_loop()
           executor = ThreadPoolExecutor()
           result = loop.run_in_executor(executor, run_async_main, query)  
           return 200, {
               "message": "Success",
           }
        except (json.JSONDecodeError):
            return {"error": "Restaurant not found"}
        
    @http_post('/restaurant_details', response={200: Dict, 400: Dict})
    async def restaurant_details_for_yelp(self,request, data: Yelp):
        """Return restaurant details for a specific ID"""
        try:
           query = data.query
           print(query)
           executor = ThreadPoolExecutor()
           future = executor.submit(forward_to_yelp,query )
        #    loop = asyncio.get_event_loop()
        #    executor = ThreadPoolExecutor()
        #    result = loop.run_in_executor(executor, run_async_main, query)  
           return 200, {
               "message": "Success",
           }
        except (json.JSONDecodeError):
            return {"error": "Restaurant not found"}
        
    @http_get('/restaurant_details', response={200: Dict, 400: Dict})
    def get_restaurant_details(self,request):
        """Return restaurant details for a specific ID"""
        try:
            print("Fetching data from yelp")
            data = fetch_yelp_data()
            return 200, data
        except Exception as e:
            return 400, {"error": str(e)}

# Register controllers
yelp_api.register_controllers(YelpController)
