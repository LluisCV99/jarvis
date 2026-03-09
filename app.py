from flask import Flask, render_template, request, jsonify
from supervisor.jarvis import jarvis_compiled
from system.commands import handle_command

app = Flask(__name__)


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
        "messages": [{"role": "user", "content": user_message}],
    }

    try:
        result = jarvis_compiled.invoke(inputs)
        response_text = result["messages"][-1].content
    except Exception as e:
        response_text = f"Error: {str(e)}"

    return jsonify({"response": response_text})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
