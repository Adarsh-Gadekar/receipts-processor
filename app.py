from flask import Flask, request, jsonify
import uuid
import re
from datetime import datetime
import math

app = Flask(__name__)

# In-memory storage for receipts and their points
receipts = {}

# Helper function to calculate points
def calculate_points(receipt):
    points = 0

    # Rule 1: One point for every alphanumeric character in the retailer name
    retailer_name = receipt['retailer']
    points += len(re.sub(r'[^a-zA-Z0-9]', '', retailer_name))

    # Rule 2: 50 points if the total is a round dollar amount with no cents
    total = float(receipt['total'])
    if total == int(total):
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if total % 0.25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt
    items = receipt['items']
    points += (len(items) // 2) * 5

    # Rule 5: If the trimmed length of the item description is a multiple of 3,
    # multiply the price by 0.2 and round up to the nearest integer
    for item in items:
        description = item['shortDescription'].strip()
        if len(description) % 3 == 0:
            price = float(item['price'])
            points += math.ceil(price * 0.2)

    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt['purchaseDate'], "%Y-%m-%d")
    if purchase_date.day % 2 == 1:
        points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = datetime.strptime(receipt['purchaseTime'], "%H:%M").time()
    if datetime.strptime("14:00", "%H:%M").time() < purchase_time < datetime.strptime("16:00", "%H:%M").time():
        points += 10

    return points

# Endpoint to process receipts
@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    receipt = request.get_json()
    receipt_id = str(uuid.uuid4())
    receipts[receipt_id] = receipt
    return jsonify({"id": receipt_id}), 200

# Endpoint to get points for a receipt
@app.route('/receipts/<string:id>/points', methods=['GET'])
def get_points(id):
    if id not in receipts:
        return jsonify({"error": "No receipt found for that ID."}), 404
    points = calculate_points(receipts[id])
    return jsonify({"points": points}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)