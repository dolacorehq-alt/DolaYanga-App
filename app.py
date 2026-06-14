import datetime
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for transactions (replace with a database in production)
transactions = []

def get_current_timestamp():
    """Return the current timestamp in ISO 8601 format."""
    return datetime.datetime.utcnow().isoformat() + "Z"

def sort_transactions_desc(transactions_list):
    """
    Sort transactions by `createdAt` in descending order.
    If a transaction lacks `createdAt`, assign the current timestamp.
    """
    for txn in transactions_list:
        if "createdAt" not in txn or not txn["createdAt"]:
            txn["createdAt"] = get_current_timestamp()
    # Sort by timestamp (newest first)
    return sorted(
        transactions_list,
        key=lambda t: datetime.datetime.fromisoformat(t["createdAt"].replace("Z", "")),
        reverse=True,
    )

@app.route("/transactions", methods=["GET"])
def list_transactions():
    """
    Return the list of transactions sorted by timestamp (newest first).
    """
    sorted_txns = sort_transactions_desc(transactions)
    return jsonify(sorted_txns), 200

@app.route("/transactions", methods=["POST"])
def create_transaction():
    """
    Create a new transaction. If `createdAt` is missing, set it to the current time.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Ensure createdAt exists
    if "createdAt" not in data or not data["createdAt"]:
        data["createdAt"] = get_current_timestamp()

    transactions.append(data)
    return jsonify(data), 201

if __name__ == "__main__":
    app.run(debug=True)
