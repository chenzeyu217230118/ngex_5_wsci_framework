from pathlib import Path
from ollama import chat

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

context = ""

for file in Path("knowledge").glob("*.txt"):
    context += file.read_text()
    context += "\n\n"

print("Context characters:", len(context))

response = chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "system",
            "content": "You are a university IT support assistant. Use only the provided context to answer the student's question."
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:\n{question}"
        }
    ]
)

print(response.message.content)