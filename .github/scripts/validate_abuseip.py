import os
import time
import requests
from datetime import datetime

# Paths
LIST_PATH = "data/malignas.txt"
BACKUP_FOLDER = "data/backups"

# Read API keys from GitHub Secrets (comma-separated)
API_KEYS = os.getenv("API_KEYS", "").split(",")

if not API_KEYS or API_KEYS == [""]:
    raise Exception("No API keys found in environment variable API_KEYS")

# AbuseIPDB endpoint
ENDPOINT = "https://api.abuseipdb.com/api/v2/check"

# Ensure backup folder exists
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# Load IP list
with open(LIST_PATH, "r") as f:
    original_ips = [line.strip() for line in f if line.strip()]

# Backup original file
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
backup_path = f"{BACKUP_FOLDER}/malignas_{timestamp}.txt"

with open(backup_path, "w") as backup:
    backup.write("\n".join(original_ips))

print(f"[INFO] Backup created: {backup_path}")

cleaned_ips = []  # IPs that are still malicious

# Rate limits: 1000 IP/day per key
max_per_key = 1000
total_allowed = len(API_KEYS) * max_per_key

print(f"[INFO] API keys loaded: {len(API_KEYS)}")
print(f"[INFO] Total IPs allowed per day: {total_allowed}")
print(f"[INFO] Total IPs in list: {len(original_ips)}")

def check_ip(ip, key):
    headers = {"Key": key, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": 90}

    try:
        r = requests.get(ENDPOINT, headers=headers, params=params, timeout=10)
        data = r.json()

        if "data" not in data:
            print(f"[ERROR] Invalid response for {ip}: {data}")
            return False

        # AbuseScore 0–100 (100 = muy malicioso)
        score = data["data"]["abuseConfidenceScore"]
        print(f"[INFO] IP {ip} → Score {score}")

        return score > 0

    except Exception as e:
        print(f"[ERROR] Exception checking {ip}: {e}")
        return True  # Si falla la consulta, mantenemos la IP por seguridad

# Process IPs distributing load across keys
index = 0
for key in API_KEYS:
    print(f"[INFO] Using API key chunk {API_KEYS.index(key)+1}/{len(API_KEYS)}")

    chunk = original_ips[index:index + max_per_key]

    for ip in chunk:
        malicious = check_ip(ip, key)
        if malicious:
            cleaned_ips.append(ip)
        time.sleep(1.2)  # evitar rate-limit

    index += max_per_key

    if index >= len(original_ips):
        break

# Save updated list
with open(LIST_PATH, "w") as f:
    f.write("\n".join(cleaned_ips))

print(f"[INFO] Updated malicious IP list saved.")
print(f"[INFO] Original: {len(original_ips)} → Active malicious: {len(cleaned_ips)}")

