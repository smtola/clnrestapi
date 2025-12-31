import json
from datetime import datetime

# Load your current ports JSON
with open("ports.json", "r") as f:
    ports = json.load(f)

# Add extra fields
for port in ports:
    port["source"] = "manual"
    port["active"] = True
    port["created_at"] = datetime.utcnow().isoformat() + "Z"

# Save to new JSON
with open("ports_ready.json", "w") as f:
    json.dump(ports, f, indent=2)

print("✅ ports_ready.json created with extra fields")
