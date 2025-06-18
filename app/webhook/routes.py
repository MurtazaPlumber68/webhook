from flask import Blueprint, request, jsonify, render_template
from app.extensions import mongo
from datetime import datetime, timedelta
import json

webhook = Blueprint('Webhook', __name__, url_prefix='')

@webhook.route('/webhook/receiver', methods=["POST"])
def receiver():
    payload = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    print(f"Received {event_type} event:")
    print(json.dumps(payload, indent=2))
    
    if event_type == 'push':
        process_push_event(payload)
    elif event_type == 'pull_request':
        process_pull_request_event(payload)
    else:
        print(f"Unsupported event type: {event_type}")
        return jsonify({"error": "Unsupported event type"}), 400
    
    return jsonify({"message": "Event processed successfully"}), 200

def process_pull_request_event(payload):
    action = payload['action']
    if action == 'closed' and payload['pull_request']['merged']:
        author = payload['pull_request']['merged_by']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        
        event_data = {
            "type": "MERGE",
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
        
        mongo.db.events.insert_one(event_data)
        print(f"Processed merge event: {event_data}")
    elif action == 'opened':
        author = payload['pull_request']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        
        event_data = {
            "type": "PULL_REQUEST",
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
        
        mongo.db.events.insert_one(event_data)
        print(f"Processed pull request event: {event_data}")

def process_push_event(payload):
    # Check if this push is associated with a recent merge
    recent_merge = mongo.db.events.find_one({
        "type": "MERGE",
        "timestamp": {"$gte": (datetime.utcnow() - timedelta(seconds=5)).strftime("%d %B %Y - %I:%M %p UTC")}
    })
    
    if recent_merge:
        print("Ignoring push event associated with recent merge")
        return
    
    author = payload['pusher']['name']
    to_branch = payload['ref'].split('/')[-1]
    timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
    
    event_data = {
        "type": "PUSH",
        "author": author,
        "to_branch": to_branch,
        "timestamp": timestamp
    }
    
    mongo.db.events.insert_one(event_data)
    print(f"Processed push event: {event_data}")

@webhook.route('/')
def index():
    return render_template('index.html')

@webhook.route('/webhook/events')
def get_events():
    events = list(mongo.db.events.find({}, {'_id': 0}).sort('timestamp', 1).limit(10))
    return jsonify(events)