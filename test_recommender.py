from app.recommender import recommend

for zone, hour, day in [(6, 18, 2), (4, 18, 2), (9, 3, 2)]:
    result = recommend(zone, hour, day)
    print(result["message"])
    for o in result["options"]:
        print("   ", o)
    print()