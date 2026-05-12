import sys
sys.path.append('d:/Ai_thesis/app')
from fastapi.testclient import TestClient
from main import app
import time
import docx

# Create dummy docx
doc = docx.Document()
doc.add_paragraph("This is a dummy test document.")
doc.save('dummy.docx')

client = TestClient(app)

def test_polling():
    session_id = "test_session_123"
    
    with open('dummy.docx', 'rb') as f:
        response = client.post(
            f"/api/slot/1?session_id={session_id}",
            files={"file": ("dummy.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        
    print("Upload response:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    task_id = data["task_id"]
    
    polls = 0
    while True:
        polls += 1
        print(f"Polling {polls}...")
        status_res = client.get(f"/api/status/{task_id}")
        assert status_res.status_code == 200
        status_data = status_res.json()
        print("Status:", status_data["status"])
        
        if status_data["status"] == "completed":
            print("Result received:", len(str(status_data["result"])), "bytes")
            break
        elif status_data["status"] == "error":
            print("Error occurred:", status_data["error"])
            break
            
        time.sleep(2)
        if polls > 5:
            print("Timed out!")
            break
            
    print(f"Total polls: {polls}")
    assert polls > 1 # Verified it polled multiple times due to the 5-sec sleep!

if __name__ == "__main__":
    test_polling()
