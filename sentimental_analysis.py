
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

# # # Example usage
# # data = get_unique_yelp_urls("yelp ovolo hong kong")
# # for url in data:
# #     print(url)
# # print(get_unique_yelp_urls("yelp shakey's pizza los angeles"))
# # print(get_longest_url("yelp ovolo hong kong"))


# # from googlesearch import search

# # def search_query(query, num_results=10):
# #     return list(search(query, num_results=num_results))

# # # Example
# # for url in search_query("yelp ovolo hong kong"):
# #     print(url)


# # from myapp.dbOperations import select_name_from_trip_business_details


# # data = select_name_from_trip_business_details("shakey's pizza parlor")
# # print(data)

# # import re

# # result = "https://www.yelp.com/biz/shakeys-pizza-parlor-pico-rivera-2"
# # # Remove protocol and domain
# # slug_path = re.sub(r"^https?://(www\.)?yelp\.com/", "", result)
# # # Replace remaining slashes with dashes
# # restaurant_slug = slug_path.replace("/", "-")
# # print(restaurant_slug)


# # import requests
# # import json

# # url = "https://www.tripadvisor.com/data/graphql/ids"

# # payload = json.dumps([
# #   {
# #     "variables": {
# #       "verifiedOnly": False,
# #       "limit": 100,
# #       "offset": 0
# #     },
# #     "extensions": {
# #       "preRegisteredQueryId": "24076282f3106d7f"
# #     }
# #   }
# # ])
# # headers = {
# #   'accept': '*/*',
# #   'accept-language': 'en-US,en;q=0.9',
# #   'content-type': 'application/json',
# #   'cookie': 'TAUnique=%1%enc%3AQbzu0H%2B%2FdN5DrdDUmc7nhKa6w7GbOGOT6fFVSFdisOMpmJSAefdkhixJHYINeLEjNox8JbUSTxk%3D; TASameSite=1; TASSK=enc%3AAHvuHii7wfzVKt7Pk%2BTW3Cu4HUzLck06zFjH3dgFoBf5o8mm76v%2BcO2V2xd%2BaH5AXzg5BfJQSObho3cCSj2Nr2IRQLB%2Biauyuiy6uswPpVsXig3IyH%2B6reqH%2Bq2go7usqA%3D%3D; TATrkConsent=eyJvdXQiOiJTT0NJQUxfTUVESUEiLCJpbiI6IkFEVixBTkEsRlVOQ1RJT05BTCJ9; TADCID=BUrST7A4BZifq4Y5ABQCrj-Ib21-TgWwDB4AzTFpg3_WsqgDA0oG_1jx3zYWUI0RCxc9gNW9I7dNHh3vxMP9C6qZhQXV4tmqx8k; PAC=AIZtCs-rZ-5xiuBYDEVIErgcNqSFivkU0UKP6sW9jCd5JkC5rhZfqx-ZNw5MCkfVY1utq6FNPgRAOYY40NqQb9bjZKNe2SkqquFopXa07VXXR0xlv2SJdHQpl2AbJJasikPR3YeQo1G0iLB2qb5ag0MaT_m0RaEiuxN1cC1-LMLJ4NxrGo43YgSq99vfUMTPA4XEAUIVBiMFDUCeVIyqlaYeFqghPgkr3QqccN6n5SqA; SRT=TART_SYNC; ServerPool=C; PMC=V2*MS.100*MD.20240808*LD.20240826; TART=%1%enc%3AvKXA3LfpKc3ZgSM9QfU8xt793aeB59Jhp%2BU%2Bj3TtZ5ayIOaOoIhK52wJdGn%2FQGZdJ7r1iEgl44g%3D; TATravelInfo=V2*A.2*MG.-1*HP.2*FL.3*RS.1; TASID=C63DC0EA9AE442A8A12575CD02C362E7; G_AUTH2_MIGRATION=informational; _gcl_au=1.1.1469864547.1724696010; _ga=GA1.1.1139279017.1724696010; roybatty=TNI1625!ANgw5Gby6eNTudh6ISUwTE8TzlmM77sozXZNHNPn%2Bj7aenI8ywyBdDEeDCrWSHK1cmBkU%2BGc5dV31kXF%2B4NoPL1xElO4X1qLxoGufyVlwW%2BdFyLK4OQKqFrlDCbqDVjwEnyd%2BhQJv1LBNTSJL0wH0kSGtCc5zLS0V%2F6suZ5Kx86B3KfWFjreUIcmumcvE2G7Bw%3D%3D%2C1; _ga_QX0Q50ZC9P=GS1.1.1724696009.1.1.1724696171.30.0.0; TAAUTHEAT=fQhLrLT9CEaLhlNlABQCS_DXENAPSyOjZ55LXtF4ZD-ttU6quw8m33kTEXS9-_OxaQtJ09l0rsM0YMwenBVXtMOXZhgZHCKGO392DHoKM72zwS3aBRN0CV_3hNyMZPqc0cXnRvq3JGvGFL4Ii_pA3bWEwTB16YES63yYCxfOCZDYZY94WSiCW_osiOCCvwf_7ZcwIlPS0ekgyTfA4nmFAwlV5fp2QzMjOvVq; __vt=UTMeynlkOIwZ0mhNABQCjdMFtf3dS_auw5cMBDN7SS-0VZbo1QfCNlckUb2j5BeZRJNpmrM8uNW62-1qscMiae2T7dReBXZXIebKp5K4pZRURyLtmna__-ZMFO4O1ndjxnycPbshPx_xBBrifppnhfEmul0UBk6YagXSkblLrDjlYaUR-Bu1RAdpUQl_1gdjxVw2eJtLW9Kuqkm7v0MMm6F8T6pllQV-vmEz2800aROacR0rxhN4sIpVj9bhR_rZvw; TASession=V2ID.C63DC0EA9AE442A8A12575CD02C362E7*SQ.39*LS.RegistrationController*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.EFE6ED236BC891EF0E24DC5ADDDDDBF6*FA.1*DF.0*TRA.true*LD.10238207*EAU.3; TAUD=LA-1724696045389-1*RDD-1-2024_08_26*LG-231994-2.1.F.*LD-231995-.....; datadome=~J2Jp3MZwADTjepxzi0erkydgr1bnBPwSnBG7lHsQq2RGDzZa1mtF6a250rCQR2X5O9A7ZOX~cplocCdnXqgRIWr7dbDY6YNCCrHMnSgbzvguI_KSXmxIXnfPYVFUIlz; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Aug+26+2024+23%3A18%3A00+GMT%2B0500+(Pakistan+Standard+Time)&version=202405.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=EFE6ED236BC891EF0E24DC5ADDDDDBF6&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false&isAnonUser=1; _gcl_aw=GCL.1724696281.null'
# # }

# # response = requests.request("POST", url, headers=headers, data=payload)

# # print(response.text)


# import subprocess
# from urllib.parse import urlparse, unquote



# def slugify_path(restaurant_url):
#     parsed = urlparse(restaurant_url)
#     path = parsed.path  # e.g., "/biz/the-sheung-wan-by-ovolo-%E9%A6%99%E6%B8%AF"
#     decoded_path = unquote(path)  # → "/biz/the-sheung-wan-by-ovolo-香港"
#     cleaned = decoded_path.strip("/").replace("/", "-")  # → "biz-the-sheung-wan-by-ovolo-香港"
    
#     if not cleaned.startswith("biz-"):
#         cleaned = "biz-" + cleaned

#     return f"{cleaned}.html"
# def execute_bash_script(restaurant_url):
#     output_filename = slugify_path(restaurant_url)

#     result = subprocess.run(
#         ['./run_curl.sh', restaurant_url, output_filename],
#         capture_output=True,
#         text=True
#     )

#     if result.returncode == 0:
#         print("Script executed successfully!")
#         print("Output:", result.stdout)
#     else:
#         print("Error executing the script.")
#         print("Error:", result.stderr)


# print(slugify_path('https://yelp.com/biz/the-sheung-wan-by-ovolo-%E9%A6%99%E6%B8%AF'))

# # def get_unique_yelp_urls(query, num_results=10):
# #     urls = list(search(query, num_results=num_results))
# #     yelp_urls = set()
    
# #     for url in urls:
# #         if "yelp.com/biz/" in url:
# #             parsed = urlparse(url)
# #             clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
# #             yelp_urls.add(clean_url)
    
# #     return list(yelp_urls)


# # print(get_unique_yelp_urls('yelp ovolo hong kong'))
import psycopg2  
import sys 
import json
from datetime import datetime
from decimal import Decimal
from psycopg2.extras import execute_values
from myapp.environment import Scraping
import googlemaps

Scraping = Scraping


def select_restaurant_names():
    conn = psycopg2.connect(
        dbname=Scraping["Database"],
        user=Scraping["Username"],
        password=Scraping["Password"],
        host=Scraping["Host"],
        port=Scraping["Port"]
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT restaurant_name FROM trip_business_details group by restaurant_name")
    
    results = cursor.fetchall()
    names = [row[0] for row in results]  # Extract names from tuples
    
    cursor.close()
    conn.close()
    
    return names

print(select_restaurant_names())