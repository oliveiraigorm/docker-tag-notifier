import requests
import json
import os

# Docker repository to track (e.g., 'library/nextcloud')
DOCKER_REPO = "library/nextcloud"

# Pushbullet API URL and Access Token (from GitHub Secrets)
PUSHBULLET_API_URL = "https://api.pushbullet.com/v2/pushes"
PUSHBULLET_ACCESS_TOKEN = os.getenv("PUSHBULLET_ACCESS_TOKEN")
PUSHBULLET_CHANNEL_TAG = os.getenv("PUSHBULLET_CHANNEL_TAG")

# Last tag is stored in a file between GitHub Action runs
TAG_FILE = "last_docker_tag.txt"

def get_latest_docker_tag(repo):
    url = f"https://hub.docker.com/v2/repositories/{repo}/tags/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Get the latest tag (assuming it's the first in the results)
        return data['results'][0]['name']
    else:
        raise Exception(f"Error fetching tags for {repo}: {response.status_code}")

def send_pushbullet_notification(tag):
    message = f"New Docker tag released for {DOCKER_REPO}: {tag}"
    data = {
        "type": "note",
        "title": "Docker Tag Update",
        "body": message,
        "channel_tag": PUSHBULLET_CHANNEL_TAG
    }
    headers = {
        "Access-Token": PUSHBULLET_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.post(PUSHBULLET_API_URL, data=json.dumps(data), headers=headers)
    if response.status_code != 200:
        print(f"Error sending Pushbullet notification: {response.status_code}, {response.text}")
    else:
        print(f"Notification sent: {message}")

def read_last_tag():
    try:
        with open(TAG_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def write_last_tag(tag):
    with open(TAG_FILE, 'w') as f:
        f.write(tag)

def main():
    last_tag = read_last_tag()
    try:
        latest_tag = get_latest_docker_tag(DOCKER_REPO)
        if latest_tag != last_tag:
            send_pushbullet_notification(latest_tag)
            write_last_tag(latest_tag)
        else:
            print("No new tag detected.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
