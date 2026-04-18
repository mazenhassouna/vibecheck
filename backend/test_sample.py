"""
Test script with sample Instagram data to verify the compatibility analyzer.
Run this to test the scoring algorithm without actual Instagram exports.

KEY TEST: Identical data MUST yield 100% compatibility.
"""

import json
import copy
from analyzer import analyze_compatibility
from scoring_config import SCORING_CONFIG, validate_config

# Sample data for Person A
sample_data = {
    "likes": [
        {"account": "natgeo", "content": "Beautiful landscape"},
        {"account": "foodnetwork", "content": "Recipe video"},
        {"account": "nike", "content": "New sneakers"},
        {"account": "spotify", "content": "Playlist"},
        {"account": "travelandleisure", "content": "Travel tips"},
    ],
    "saved": [
        {"account": "cooking_with_chef", "url": "https://instagram.com/p/abc123"},
        {"account": "travelblogger", "url": "https://instagram.com/p/def456"},
        {"account": "fitnesscoach", "url": "https://instagram.com/p/ghi789"},
    ],
    "following": [
        {"username": "natgeo"},
        {"username": "foodnetwork"},
        {"username": "nike"},
        {"username": "spotify"},
        {"username": "travelandleisure"},
        {"username": "therock"},
        {"username": "kevinhart4real"},
        {"username": "nasa"},
    ],
    "topics": [
        {"name": "Travel"},
        {"name": "Photography"},
        {"name": "Food"},
        {"name": "Fitness"},
        {"name": "Music"},
    ],
    "comments": [
        {"length": 25, "has_emoji": True, "has_question": False, "word_count": 5},
        {"length": 30, "has_emoji": True, "has_question": True, "word_count": 6},
        {"length": 15, "has_emoji": False, "has_question": False, "word_count": 3},
        {"length": 40, "has_emoji": True, "has_question": False, "word_count": 8},
    ],
}

# Different data for comparison testing
different_data = {
    "likes": [
        {"account": "bbcearth", "content": "Wildlife photo"},
        {"account": "patagonia", "content": "Outdoor gear"},
    ],
    "saved": [
        {"account": "hikingtrails", "url": "https://instagram.com/p/xyz999"},
    ],
    "following": [
        {"username": "bbcearth"},
        {"username": "patagonia"},
        {"username": "chrisburkard"},
    ],
    "topics": [
        {"name": "Nature"},
        {"name": "Adventure"},
        {"name": "Hiking"},
    ],
    "comments": [
        {"length": 100, "has_emoji": False, "has_question": True, "word_count": 20},
        {"length": 120, "has_emoji": False, "has_question": True, "word_count": 25},
    ],
}


def run_identical_test():
    """Test that identical data yields 100% compatibility."""
    print("=" * 60)
    print("TEST 1: Identical Data → Should be 100%")
    print("=" * 60)
    
    person_a = copy.deepcopy(sample_data)
    person_b = copy.deepcopy(sample_data)  # Exact copy
    
    result = analyze_compatibility(person_a, person_b)
    
    print(f"\n🎯 SCORE: {result['score']}%")
    print(f"   Expected: 100%")
    print(f"   Status: {'✓ PASS' if result['score'] == 100 else '✗ FAIL'}")
    
    print("\n--- Category Breakdown ---")
    for category, data in result['breakdown'].items():
        status = "✓" if data['score'] == 100.0 else "✗"
        print(f"  {status} {category.capitalize():12} {data['score']:5.1f}% (expected 100%)")
    
    return result['score'] == 100


def run_empty_data_test():
    """Test that two empty datasets yield 100% (both identical)."""
    print("\n" + "=" * 60)
    print("TEST 2: Empty Data → Should be 100% (identical empty)")
    print("=" * 60)
    
    person_a = {"likes": [], "saved": [], "following": [], "topics": [], "comments": []}
    person_b = {"likes": [], "saved": [], "following": [], "topics": [], "comments": []}
    
    result = analyze_compatibility(person_a, person_b)
    
    print(f"\n🎯 SCORE: {result['score']}%")
    print(f"   Expected: 100%")
    print(f"   Status: {'✓ PASS' if result['score'] == 100 else '✗ FAIL'}")
    
    return result['score'] == 100


def run_different_data_test():
    """Test that completely different data yields low compatibility."""
    print("\n" + "=" * 60)
    print("TEST 3: Completely Different Data → Should be < 50%")
    print("=" * 60)
    
    result = analyze_compatibility(sample_data, different_data)
    
    print(f"\n🎯 SCORE: {result['score']}%")
    print(f"   Expected: < 50%")
    print(f"   Status: {'✓ PASS' if result['score'] < 50 else '✗ FAIL'}")
    
    print("\n--- Category Breakdown ---")
    for category, data in result['breakdown'].items():
        print(f"  {category.capitalize():12} {data['score']:5.1f}%")
    
    return result['score'] < 50


def run_partial_overlap_test():
    """Test partial overlap scenario."""
    print("\n" + "=" * 60)
    print("TEST 4: Partial Overlap → Should be between 20-80%")
    print("=" * 60)
    
    # Create data with some overlap
    person_a = copy.deepcopy(sample_data)
    person_b = {
        "likes": [
            {"account": "natgeo"},  # Same
            {"account": "spotify"},  # Same
            {"account": "newaccount1"},
            {"account": "newaccount2"},
        ],
        "saved": [
            {"account": "travelblogger", "url": "https://instagram.com/p/def456"},  # Same
            {"account": "different_account"},
        ],
        "following": [
            {"username": "natgeo"},  # Same
            {"username": "nasa"},    # Same
            {"username": "different1"},
            {"username": "different2"},
        ],
        "topics": [
            {"name": "Travel"},      # Same
            {"name": "Photography"}, # Same
            {"name": "Tech"},
        ],
        "comments": [
            {"length": 25, "has_emoji": True, "has_question": False, "word_count": 5},  # Similar style
        ],
    }
    
    result = analyze_compatibility(person_a, person_b)
    
    print(f"\n🎯 SCORE: {result['score']}%")
    print(f"   Expected: 20-80%")
    print(f"   Status: {'✓ PASS' if 20 <= result['score'] <= 80 else '✗ FAIL'}")
    
    print("\n--- Category Breakdown ---")
    for category, data in result['breakdown'].items():
        print(f"  {category.capitalize():12} {data['score']:5.1f}%")
    
    return 20 <= result['score'] <= 80


def run_all_tests():
    print("\n" + "=" * 60)
    print("Instagram Compatibility Analyzer - Test Suite")
    print("=" * 60)
    
    # Validate config first
    try:
        validate_config()
        print("✓ Config validation passed")
    except ValueError as e:
        print(f"✗ Config validation failed: {e}")
        return
    
    tests = [
        ("Identical Data Test", run_identical_test),
        ("Empty Data Test", run_empty_data_test),
        ("Different Data Test", run_different_data_test),
        ("Partial Overlap Test", run_partial_overlap_test),
    ]
    
    results = []
    for name, test_func in tests:
        passed = test_func()
        results.append((name, passed))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED - Review output above")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
