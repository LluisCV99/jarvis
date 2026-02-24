from flask import Flask, render_template, request, jsonify
from jarvis import jarvis_compiled, JARVIS_SYSTEM_PROMPT
from langchain_core.messages import HumanMessage, SystemMessage
from system.commands import handle_command

app = Flask(__name__)

with open("prompts/jarvis.md", 'r') as f:
    jarvis_prompt = f.read()

@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Intercept slash commands before sending to the LLM
    is_command, response_text = handle_command(user_message)
    if is_command:
        return jsonify({"response": response_text})

    inputs = {
        "messages": [
            SystemMessage(content=jarvis_prompt),
            SystemMessage(content=JARVIS_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ],
        "errors": [],
        "max_calls": 6,
        "call_count": 0,
    }

    try:
        result = jarvis_compiled.invoke(inputs)
        response_text = result["messages"][-1].content
    except Exception as e:
        response_text = f"Error: {str(e)}"

    return jsonify({"response": response_text})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
