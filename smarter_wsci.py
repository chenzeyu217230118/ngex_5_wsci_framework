from pathlib import Path
import json
from ollama import chat

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""


def select_context(question: str) -> list[str]:
    keywords = {
        "wifi": ["wi-fi", "wifi", "eduroam", "wireless"],
        "password": ["password", "credential", "login", "authenticate"],
        "service": ["status", "outage", "operational"],
        "vpn": ["vpn"],
        "print": ["print", "printer"],
        "email": ["email", "mail"],
        "projector": ["projector", "display", "hdmi"],
    }

    question_lower = question.lower()
    selected = set()

    if any(k in question_lower for k in keywords["wifi"]):
        selected.add("knowledge/wifi_setup.txt")
    if any(k in question_lower for k in keywords["password"]):
        selected.add("knowledge/password_changes.txt")
    if any(k in question_lower for k in keywords["service"]):
        selected.add("knowledge/service_status.txt")
    if any(k in question_lower for k in keywords["vpn"]):
        selected.add("knowledge/vpn.txt")
    if any(k in question_lower for k in keywords["print"]):
        selected.add("knowledge/printing.txt")
    if any(k in question_lower for k in keywords["email"]):
        selected.add("knowledge/email_setup.txt")
    if any(k in question_lower for k in keywords["projector"]):
        selected.add("knowledge/classroom_projectors.txt")

    return sorted(selected)


selected_files = select_context(question)
print("Selected files:", selected_files)

context = ""
for file in selected_files:
    context += Path(file).read_text()
    context += "\n\n"

print("Raw context characters:", len(context))


def compress_context(context: str, question: str) -> str:
    response = chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a context compression assistant. "
                    "Extract only the information relevant to the user's question. "
                    "Return a concise, structured summary. Do not add new facts."
                )
            },
            {
                "role": "user",
                "content": f"Question:\n{question}\n\nFull context:\n{context}"
            }
        ]
    )
    return response.message.content


compressed_context = compress_context(context, question)
print("Compressed context characters:", len(compressed_context))

response = chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a university IT support assistant. "
                "Answer using only the compressed context. "
                "Return a structured answer with fields: "
                "problem, likely_cause, recommended_steps, service_status."
            )
        },
        {
            "role": "user",
            "content": f"Compressed context:\n{compressed_context}\n\nQuestion:\n{question}"
        }
    ]
)

print(response.message.content)

state = {
    "problem": question,
    "selected_files": selected_files,
    "compressed_context": compressed_context,
    "answer": response.message.content,
    "service_status": {
        "wifi": "operational"
    }
}

with open("state.json", "w") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("State written to state.json")

with open("state.json", "r") as f:
    state = json.load(f)

task_context = {
    "problem": state["problem"],
    "service_status": state["service_status"],
    "compressed_context": state["compressed_context"],
}

response = chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "system",
            "content": "Use only the provided state fields relevant to the task."
        },
        {
            "role": "user",
            "content": f"State:\n{json.dumps(task_context, ensure_ascii=False, indent=2)}\n\nQuestion:\n{state['problem']}"
        }
    ]
)

print(response.message.content)