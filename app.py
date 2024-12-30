import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

JSON_FILE_PATH = "cards.json"

def load_cards() -> dict:
    if not os.path.exists(JSON_FILE_PATH):
        return {}
    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_cards(data: dict):
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route("/get_cards", methods=["GET"])
def get_cards():
    data = load_cards()
    print("response received")
    return jsonify(data), 200

@app.route("/cards", methods=["PATCH"])
def patch_cards():
    updates = request.get_json()
    if not updates:
        return jsonify({"error": "No JSON payload provided."}), 400

    original_data = load_cards()
    new_data = merge_data(original_data, updates)
    save_cards(new_data)
    return jsonify(new_data), 200

def merge_data(original: dict, updates: dict) -> dict:
    for k, v in updates.items():
        if k not in original:
            original[k] = v
            continue

        if isinstance(original[k], dict) and isinstance(v, dict):
            merge_data(original[k], v)

        elif isinstance(original[k], list) and isinstance(v, list):
            merge_lists(original[k], v)

        else:
            original[k] = v

    return original

def merge_lists(orig_list: list, update_list: list):
    index_map = {}
    for i, item in enumerate(orig_list):
        if isinstance(item, dict) and "card_name" in item:
            index_map[item["card_name"]] = i

    for new_item in update_list:
        if "card_name" not in new_item:
            orig_list.append(new_item)
            continue

        card_name = new_item["card_name"]
        if card_name in index_map:
            idx = index_map[card_name]
            for key, val in new_item.items():
                if key == "card_name":
                    continue
                orig_list[idx][key] = val
        else:
            orig_list.append(new_item)

@app.errorhandler(404)
def page_not_found(_):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(_):
    return jsonify({"error": "Internal server error"}), 500
    
@app.before_request
def log_request():
    print(f"Received {request.method} request at {request.path}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=443)
