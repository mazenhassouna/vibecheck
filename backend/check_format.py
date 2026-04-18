#!/usr/bin/env python3
import json

base = "/home/mhassoun/Downloads/instagram-reshialkhan1-2026-04-18-jhb2u11Z"

# Check liked_posts.json
print("=== LIKED POSTS FORMAT ===")
with open(f"{base}/your_instagram_activity/likes/liked_posts.json") as f:
    data = json.load(f)
    print(f"Keys: {list(data.keys())}")
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 0:
            print(f"\n{key} - First 2 items:")
            print(json.dumps(value[:2], indent=2))

print("\n\n=== SAVED POSTS FORMAT ===")
with open(f"{base}/your_instagram_activity/saved/saved_posts.json") as f:
    data = json.load(f)
    print(f"Keys: {list(data.keys())}")
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 0:
            print(f"\n{key} - First 2 items:")
            print(json.dumps(value[:2], indent=2))
