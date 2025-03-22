from patchright.sync_api import sync_playwright
import time
import json

def search_and_log_reviews():
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # Capture review-related responses
        def capture_response(response):
            if 'https://www.google.com/maps/rpc/listugcposts?' in response.url:
                print("Captured review response.")
                try:
                    if 'application/json' in response.headers.get('content-type', ''):
                        response_data = response.json()
                        with open('gmb.json', 'w', encoding='utf-8') as f:
                            json.dump(response_data, f, ensure_ascii=False, indent=4)
                        print("Review data saved to gmb.json")
                    else:
                        print("Response is not JSON. Skipping.")
                except Exception as e:
                    print(f"Error capturing response: {e}")
        
        page.on("response", capture_response)
        
        # Navigate to Google Maps
        page.goto('https://maps.google.com')
        page.wait_for_load_state('networkidle')

        # Accept cookies if present
        if page.locator('text="Accept all"').is_visible():
            page.click('text="Accept all"')

        # Perform search
        search_box = page.locator('input[name="q"]')
        search_box.click()
        search_box.fill("Shakey's Pizza Parlor Brea")
        page.keyboard.press('Enter')
        page.wait_for_load_state('networkidle')
        print("Search results loaded")

        # Wait for the place's info panel
        page.wait_for_selector('h1:has-text("Shakey\'s Pizza")', state='visible', timeout=10000)
        print("Found Shakey's Pizza in results")

        # Click on reviews
        reviews_selector = ['button:has-text("reviews")', 'a:has-text("reviews")', '[aria-label*="reviews"]']
        clicked_reviews = False

        for selector in reviews_selector:
            if page.locator(selector).count() > 0:
                print(f"Found reviews element with selector: {selector}")
                page.locator(selector).first.click()
                clicked_reviews = True
                break

        if not clicked_reviews:
            print("Could not find reviews selector. Taking screenshot.")
            page.screenshot(path="no_reviews_found.png")
        else:
           
            time.sleep(5)
            samole_click = page.query_selector('div[class*="cVwbnc IlRKB"]')
            samole_click.click()

            # Press 'End' key to load more reviews
            print("Pressing 'End' key to load reviews...")
            for i in range(35):
                print(i)
                page.keyboard.press('End')
                time.sleep(2)

        time.sleep(5)  # Additional wait for requests
        print("Review capture completed.")
        
        browser.close()

if __name__ == "__main__":
    search_and_log_reviews()
