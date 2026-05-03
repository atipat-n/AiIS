import sys
import os

# Add parent dir to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service import call_kku_llm

# Create a long text with paragraph breaks so it gets chunked properly
# 500 paragraphs of ~25 characters each = ~12,500 characters -> ~7 chunks
long_text = "This is a test paragraph.\n\n" * 500

print("Starting extraction loop test...")
result = call_kku_llm(prompt="Summarize this", document_text=long_text)

print(f"Total chunks processed: {result['total_chunks']}")

if "⚠️ AI ทำงานหนักเกินไป" in result["feedback"]:
    print("FAILED: Hit 429 rate limit.")
    sys.exit(1)
elif "⚠️ ไม่สามารถเชื่อมต่อ" in result["feedback"]:
    print("FAILED: Connection error.")
    sys.exit(1)
else:
    print("SUCCESS: Processed all chunks without hitting rate limit.")
    sys.exit(0)
