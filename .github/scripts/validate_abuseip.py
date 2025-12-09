import os
import time
import requests
from datetime import datetime

# Paths
LIST_PATH = "data/malignas.txt"
BACKUP_FOLDER = "data/backups"
POINTER_PATH = "data/last_position.txt"

# Read API keys from GitHub Secrets (comma-separated)
API_KEYS = os.getenv("API_KEYS", "").split(",")

if not API_KEYS or API_KEYS == [""]:
    raise Exception("No API keys found in environment variable API_KEYS")

max_per_key = 1000
total_daily_allowed = len(API_KEYS) * max_per_key

# Ensure folders exist
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# Load IP list
with open(LIST_PATH, "r") as f:
    ips = [line.strip() for line in f if line.strip()]

total_ips = len(ips)

# Load last processed position
if os.path.exists(POINTER_PATH):
    with open(POINTER_PATH, "r") as f:
        last_pos = int(f.read().strip())
else:
    last_pos = 0

print(f"[INFO] Total IPs: {total_ips}")
print(f"[INFO] Last processed position: {last_pos}")
print(f"[INFO] Daily limit based on API keys: {total_daily_allowed}")

# Backup before processing
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
backup_path = f"{BACKUP_FOLDER}/malignas_{timestamp}.txt"

with open(backup_path, "w") as backup:
    backup.write("\n".join(ips))

print(f"[INFO] Backup created -> {backup_path}")

ENDPOINT = "https://api.abuseipdb.com/api/v2/check"

def check_ip(ip, key):
    headers = {"Key": key, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": 90}

    try:
        r = requests.get(ENDPOINT, headers=headers, params=params, timeout=10)
        data = r.json()
        
        if "data" not in data:
            print(f"[WARN] Invalid response for {ip}: {data}")
            return True  # preserve if unknown

        score = data["data"]["abuseConfidenceScore"]
        print(f"[INFO] {ip} → Score: {score}")
        return score > 0

    except Exception as e:
        print(f"[ERROR] Failed on {ip}: {e}")
        return True  # preserve if error

updated_ips = []
delete_counter = 0

processed = 0
position = last_pos

for key_index, key in enumerate(API_KEYS):
    print(f"[INFO] Using API key {key_index+1}/{len(API_KEYS)}")

    for _ in range(max_per_key):
        if processed >= total_daily_allowed:
            break

        # Wrap around when reaching the end
        if position >= total_ips:
            position = 0

        ip = ips[position]
        is_malicious = check_ip(ip, key)

        if is_malicious:
            updated_ips.append(ip)
        else:
            delete_counter += 1
            print(f"[INFO] IP removed: {ip}")

        processed += 1
        position += 1

        time.sleep(1.2)  # rate-limit safety

# Save updated list
with open(LIST_PATH, "w") as f:
    f.write("\n".join(updated_ips))

print(f"[INFO] Processing completed.")
print(f"[INFO] Malicious kept: {len(updated_ips)}")
print(f"[INFO] Removed (no longer malicious): {delete_counter}")

# Save new pointer
with open(POINTER_PATH, "w") as f:
    f.write(str(position))

print(f"[INFO] New position saved: {position}")
