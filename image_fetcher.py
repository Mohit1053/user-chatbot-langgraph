import os
import csv
import io
import requests
from typing import List, Dict

# === CSV path ===
FIREBASE_IMAGE_CSV_URL = os.getenv("FIREBASE_IMAGE_CSV_URL")

def load_image_data() -> List[Dict]:

    response = requests.get(FIREBASE_IMAGE_CSV_URL)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch IMAGE_DATASET CSV. Status: {response.status_code}")

    image_csv_buffer = io.StringIO(response.text)
    reader = csv.DictReader(image_csv_buffer)

    image_data = []
    for row in reader:
        image_data.append({
            "image_id": row["image_id"],
            "faq_id": row["faq_id"],
            "image_url": row["image_url"],
            "description": row["description"]
        })
    return image_data


def fetch_images_by_faq(faq_id: str) -> List[Dict]:
    """
    Fetch image(s) associated with a given FAQ ID.
    
    - If 1 image: return that single image in a list
    - If multiple: return list sorted by image_id (assumed stepwise)
    - If none: return empty list
    """
    all_images = load_image_data()

    # Filter by faq_id
    matched_images = [
        img for img in all_images if img["faq_id"] == faq_id
    ]

    if not matched_images:
        return []

    # Sort stepwise answers by image_id (assumes sortable order like img_01, img_02, ...)
    matched_images.sort(key=lambda img: img["image_id"])

    return matched_images


# === Example usage for test ===
if __name__ == "__main__":
    example_faq_id = "46"
    results = fetch_images_by_faq(example_faq_id)
    
    if results:
        print(f"\n✅ Images for FAQ ID {example_faq_id}:")
        for img in results:
            print(f"- {img['image_id']}: {img['description']} ({img['image_url']})")
    else:
        print(f"\n❌ No images found for FAQ ID {example_faq_id}.")
