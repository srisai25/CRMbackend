# from apify_client import ApifyClient

# # Initialize the ApifyClient with your Apify API token
# # Replace '<YOUR_API_TOKEN>' with your token.
# client = ApifyClient("apify_api_oLQF0YMZCa8CTOnL9Y40x6tIASOmu23AyZ5y")

# # Prepare the Actor input
# run_input = {
#     "startUrls": [{ "url": "https://www.google.com/maps/place/Yellowstone+National+Park/@44.5857951,-110.5140571,9z/data=!3m1!4b1!4m5!3m4!1s0x5351e55555555555:0xaca8f930348fe1bb!8m2!3d44.427963!4d-110.588455?hl=en-GB" }],
#     "maxReviews": 100,
#     "language": "en",
# }

# # Run the Actor and wait for it to finish
# run = client.actor("compass/google-maps-reviews-scraper").call(run_input=run_input)

# # Fetch and print Actor results from the run's dataset (if there are any)
# print("💾 Check your data here: https://console.apify.com/storage/datasets/" + run["defaultDatasetId"])
# for item in client.dataset(run["defaultDatasetId"]).iterate_items():
#     print(item)

# # 📚 Want to learn more 📖? Go to → https://docs.apify.com/api/client/python/docs/quick-start

import os
from apify_client import ApifyClient

# -----------------------------
# 🔐 1. SET YOUR API TOKEN HERE
# -----------------------------
APIFY_TOKEN = "apify_api_oLQF0YMZCa8CTOnL9Y40x6tIASOmu23AyZ5y"

# -----------------------------
# 🚀 2. INITIALIZE CLIENT
# -----------------------------
print("✅ Script started...")
client = ApifyClient(APIFY_TOKEN)

# -----------------------------
# 🌍 3. ACTOR INPUT (Google Maps URL)
# -----------------------------
run_input = {
    "startUrls": [
        {
            "url": "https://www.google.com/maps/place/McDonald's/@37.7798713,-122.5079349,13z/data=!4m7!3m6!1s0x808580bb058365f7:0xfd5ee1b75e539d41!8m2!3d37.7798713!4d-122.4317172!15sCgpNY0RvbmFsZCdzIgOIAQFaDCIKbWNkb25hbGQnc5IBFGZhc3RfZm9vZF9yZXN0YXVyYW50qgFcCg0vZy8xMWJjNmNfX3MyCgkvbS8wN2d5cDcQASoOIgptY2RvbmFsZCdzKAAyHhABIhogkCLuxcAwSYOdmRE7TT_O3KjgOIUmWtT6kDIOEAIiCm1jZG9uYWxkJ3PgAQA!16s%2Fm%2F04fjw6s"
        }
    ],
    "maxReviews": 10,
    "language": "en",
}

# -----------------------------
# 🎬 4. RUN THE ACTOR
# -----------------------------
print("Running Apify actor... ⏳")
run = client.actor("compass/google-maps-reviews-scraper").call(run_input=run_input)
print("✅ Actor finished running!")

dataset_id = run.get("defaultDatasetId")
if not dataset_id:
    print("⚠️ No dataset ID returned. Something went wrong.")
    print(run)
    exit()

# -----------------------------
# 📊 5. FETCH RESULTS
# -----------------------------
print(f"\n📦 Dataset ID: {dataset_id}")
print("\nFetching results...\n")

found = False
for i, item in enumerate(client.dataset(dataset_id).iterate_items(), start=1):
    if i == 1:
        print("🧩 Available keys in one review item:")
        print(list(item.keys()))
        print("---------------------------\n")

    found = True
    author = item.get("authorName") or item.get("userName") or item.get("name") or "Unknown"
    print(f"--- Review {i} ---")
    print(f"Author: {author}")
    print(f"Rating: {item.get('stars')}")
    print(f"Text: {item.get('text')}")
    print(f"Date: {item.get('publishAt')}")
    print("---------------------------\n")

if not found:
    print("⚠️ No reviews found. Try increasing 'maxReviews' or checking the URL.")
else:
    print("🎉 Done! Reviews fetched successfully.")
