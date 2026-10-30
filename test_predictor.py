from app.predictor import train_model, predict_all_zones

print("Training model...")
print(train_model())

print("\n--- Predicted demand: Wednesday 6 PM (hour 18, day 2) ---")
print(predict_all_zones(18, 2)[["zone_name", "predicted_rides"]])

print("\n--- Predicted demand: Wednesday 3 AM (hour 3, day 2) ---")
print(predict_all_zones(3, 2)[["zone_name", "predicted_rides"]])