import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Testing /api/ai_chunk endpoint...")

chunk_data = {
    "chunk_text": "ย่อหน้านี้มีการสะกดคำผิด เช่น อณุญาติ และ โอกาศ ซึ่งควรแก้ไขให้ถูกต้องตามหลักภาษาไทย.",
    "slot_number": 1,
    "chapter": 0,
    "chunk_index": 1,
    "total_chunks": 1
}

response = client.post("/api/ai_chunk", json=chunk_data)

if response.status_code == 200:
    res_json = response.json()
    if res_json["success"]:
        print("SUCCESS! API returned:")
        print(res_json["data"])
    else:
        print("FAILED inside API:")
        print(res_json["message"])
else:
    print(f"FAILED with status code {response.status_code}")
    print(response.text)
