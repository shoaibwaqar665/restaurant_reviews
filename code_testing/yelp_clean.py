from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, parse_qs, unquote
import re

# Load HTML file
with open("response.txt", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Helper to find meta content
def get_meta_content(soup, name):
    tag = soup.find("meta", attrs={"name": name})
    return tag["content"].strip() if tag and tag.get("content") else None

# Get meta tags
description = get_meta_content(soup, "description")
yelp_biz_id = get_meta_content(soup, "yelp-biz-id")

# Get directions address
def get_directions_address(soup):
    tag = soup.find("p", class_="y-css-qn4gww")
    if tag and tag.find("a") and "Get Directions" in tag.text:
        return tag.text.strip()
    return None

# Get phone number under <p> with text "Phone number"
def get_phone_number(soup):
    phone_tag = soup.find("p", string=lambda s: s and "Phone number" in s)
    if phone_tag:
        next_tag = phone_tag.find_next_sibling("p")
        if next_tag:
            return next_tag.text.strip()
    return None

def get_address(soup):
    phone_tag = soup.find("p", string=lambda s: s and "Get Directions" in s)
    if phone_tag:
        next_tag = phone_tag.find_next_sibling("p")
        if next_tag:
            raw_text = next_tag.text.replace("\n", "").strip()
            clean_address = re.sub(r'\s+', ' ', raw_text)
            return clean_address
    return None
# Get business website link under specific <p> class
def get_business_website(soup):
    p_tag = soup.find("p", class_="y-css-9fw56v", string="Business website")
    if p_tag:
        link = p_tag.find_next("a", href=True)
        if link:
            href = link["href"].strip()
            parsed_url = urlparse(href)
            query_params = parse_qs(parsed_url.query)
            if "url" in query_params:
                # Decode the redirected URL
                return unquote(query_params["url"][0])
            return href  # If it's already a direct URL
    return None

def get_website_menu_link(soup):
    menu_divs = soup.find_all("div", class_="y-css-6az2m0")
    for div in menu_divs:
        if div.find("span", string="Website menu"):
            link_tag = div.find("a", href=True)
            if link_tag:
                href = link_tag["href"].strip()
                parsed_url = urlparse(href)
                query_params = parse_qs(parsed_url.query)
                if "url" in query_params:
                    # Decode the redirected URL
                    return unquote(query_params["url"][0])
                return href  # If it's already a direct URL
    return None

def get_hours_of_operation(soup):
    hours_table = soup.find("table", class_="hours-table__09f24__KR8wh")
    hours = {}

    if hours_table:
        rows = hours_table.find_all("tr", class_="y-css-29kerx")
        for row in rows:
            day_tag = row.find("p", class_="day-of-the-week__09f24__JJea_")
            time_tag = row.find("p", class_="no-wrap__09f24__c3plq")
            if day_tag and time_tag:
                day = day_tag.get_text(strip=True)
                time = time_tag.get_text(strip=True)
                hours[day] = time

    return hours

def get_custom_class_data(soup):
    elements = soup.find_all("div", class_="arrange-unit__09f24__rqHTg arrange-unit-fill__09f24__CUubG y-css-1n5biw7")

    for el in elements:
        text = el.get_text(separator=" ", strip=True)
        if text:
            match = re.match(r"([\d.]+)\s+\((\d+)\s+reviews\)", text)
            if match:
                rating = match.group(1)
                review_count = match.group(2)
                
                return {
                    "rating": float(rating),
                    "review_count": int(review_count)
                }

    return {
        "rating": None,
        "review_count": None
    }


amenities = []
def get_amenities(soup):
    section = soup.find("section", {"aria-label": "Amenities and More"})


    if section:
        for item in section.select("div.arrange__09f24__LDfbs.vertical-align-baseline__09f24__fA6Jk"):
            label = item.select_one("span.y-css-qn4gww")
            value = item.select_one("span.label-spacing-v2__09f24__RiEXv")

            if label:
                if value:  # e.g., Health Score
                    amenities.append(f"{label.text.strip()}: {value.text.strip()}")
                else:  # e.g., Offers Delivery / Takeout
                    amenities.append(label.text.strip())
    data = get_vibe_check_attributes(soup)
    if data:
        for item in data:
            if item not in amenities:
                amenities.append(item)

    return amenities

def get_vibe_check_attributes(soup):
    vibe_section = soup.find("div", class_="y-css-gdh503", attrs={"data-testid": "VibeCheckAttributes"})
    
    vibe_attributes = []
    if amenities:
        # Find all the inner divs that represent each attribute (Casual, Moderate noise, etc.)
        vibe_items = vibe_section.find_all("div", class_="arrange__09f24__LDfbs")
        
        for item in vibe_items:
            # Get the label (e.g., Casual, Moderate noise, Dogs allowed)
            label_tag = item.find("span", class_="y-css-1541nhh")
            if label_tag:
                amenities.append(label_tag.text.strip())
    
    return amenities
# Final extracted data
data = {
    "meta_description": description,
    "yelp_biz_id": yelp_biz_id,
    "directions_address": get_directions_address(soup),
    "phone_number": get_phone_number(soup),
    "business_website": get_business_website(soup),
    "address": get_address(soup),
    "website_menu": get_website_menu_link(soup),
    "hours_of_operation": get_hours_of_operation(soup),
    "amenities": get_amenities(soup),
    "custom_class_data" : get_custom_class_data(soup)
    # "vibe_check_attributes": get_vibe_check_attributes(soup)  # Add vibe check attributes to the data
}

# Save to JSON
with open("cleaned_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Data extracted and saved to cleaned_data.json")
