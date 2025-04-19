from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, parse_qs, unquote
import re

from myapp.reviews_yelp_data import extract_review_yelp_data
from myapp.yelp_total_reviews import scrape_yelp_reviews
from myapp.dbOperations import InsertRestaurantDetailsForYelp

def get_meta_content(soup, name):
    tag = soup.find("meta", attrs={"name": name})
    return tag["content"].strip() if tag and tag.get("content") else None

def get_directions_address(soup):
    tag = soup.find("p", class_="y-css-qn4gww")
    if tag and tag.find("a") and "Get Directions" in tag.text:
        return tag.text.strip()
    return None

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

def get_business_website(soup):
    p_tag = soup.find("p", class_="y-css-9fw56v", string="Business website")
    if p_tag:
        link = p_tag.find_next("a", href=True)
        if link:
            href = link["href"].strip()
            parsed_url = urlparse(href)
            query_params = parse_qs(parsed_url.query)
            return unquote(query_params["url"][0]) if "url" in query_params else href
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
                return unquote(query_params["url"][0]) if "url" in query_params else href
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
                hours[day_tag.get_text(strip=True)] = time_tag.get_text(strip=True)
    return hours

def get_custom_class_data(soup):
    elements = soup.find_all("div", class_="arrange-unit__09f24__rqHTg arrange-unit-fill__09f24__CUubG y-css-1n5biw7")
    for el in elements:
        text = el.get_text(separator=" ", strip=True)
        match = re.match(r"([\d.]+)\s+\((\d+)\s+reviews\)", text)
        if match:
            return {
                "rating": float(match.group(1)),
                "review_count": int(match.group(2))
            }
    return {"rating": None, "review_count": None}

def get_vibe_check_attributes(soup):
    vibe_section = soup.find("div", class_="y-css-gdh503", attrs={"data-testid": "VibeCheckAttributes"})
    vibe_attributes = []
    if vibe_section:
        vibe_items = vibe_section.find_all("div", class_="arrange__09f24__LDfbs")
        for item in vibe_items:
            label_tag = item.find("span", class_="y-css-1541nhh")
            if label_tag:
                vibe_attributes.append(label_tag.text.strip())
    return vibe_attributes

def get_amenities(soup):
    amenities = []
    section = soup.find("section", {"aria-label": "Amenities and More"})
    if section:
        for item in section.select("div.arrange__09f24__LDfbs.vertical-align-baseline__09f24__fA6Jk"):
            label = item.select_one("span.y-css-qn4gww")
            value = item.select_one("span.label-spacing-v2__09f24__RiEXv")
            if label:
                amenities.append(f"{label.text.strip()}: {value.text.strip()}" if value else label.text.strip())
    vibe_attrs = get_vibe_check_attributes(soup)
    for item in vibe_attrs:
        if item not in amenities:
            amenities.append(item)
    return amenities

def parse_yelp_html(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    return {
        "meta_description": get_meta_content(soup, "description"),
        "yelp_biz_id": get_meta_content(soup, "yelp-biz-id"),
        "directions_address": get_directions_address(soup),
        "phone_number": get_phone_number(soup),
        "business_website": get_business_website(soup),
        "address": get_address(soup),
        "website_menu": get_website_menu_link(soup),
        "hours_of_operation": get_hours_of_operation(soup),
        "amenities": get_amenities(soup),
        "custom_class_data": get_custom_class_data(soup)
    }

def yelp_loc_clean(input_file, output_file, query, location):
    try:
        whole_data = parse_yelp_html(input_file)

        if not whole_data:
            raise ValueError("Parsed data is None or empty")

        InsertRestaurantDetailsForYelp(whole_data, query, location)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(whole_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Data extracted and saved to {output_file}")

        address = whole_data.get("address", "N/A")
        review_count = whole_data.get("custom_class_data", {}).get("review_count", "0")
        yelp_biz_id = whole_data.get("yelp_biz_id", "N/A")

        print("Address:", address)
        print("Review Count:", review_count)
        print("Yelp Biz ID:", yelp_biz_id)

        business_key = f"{location}{address}{query}".replace(" ", "_").replace(",", "")

        if yelp_biz_id == "N/A" or review_count == 0:
            raise ValueError("Invalid Yelp Business ID or review count is zero")

        raw_data = scrape_yelp_reviews(yelp_biz_id, review_count, output_file=f"{business_key}_raw.json")

        if not raw_data:
            raise ValueError("No review data returned from scraper")

        extract_review_yelp_data(raw_data, f"{business_key}_reviews.json", business_key, yelp_biz_id)
        print(f"🎉 Data extraction completed and saved to {output_file}")

    except FileNotFoundError:
        print(f"❌ Error: The file {input_file} was not found.")
    except json.JSONDecodeError:
        print("❌ Error: Failed to decode JSON data.")
    except ValueError as ve:
        print(f"❌ Value Error: {ve}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")