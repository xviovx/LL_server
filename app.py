from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import os

# env vars
load_dotenv(".env")
openai.api_key = os.environ["API_KEY"]

# flast app
app = Flask(__name__)
CORS(app)

# default mode for bot and conversation history
current_mode = "formal"
conversation_history = []

@app.route('/change-mode', methods=['POST'])
def change_mode():
    global current_mode
    global conversation_history  # reset conversation history when mode changes
    conversation_history = []
    mode = request.json.get('mode')
    print(f"Attempting to change mode to: {mode}")
    if mode in ["formal", "playful"]:
        current_mode = mode
        return jsonify({"message": f"Mode changed to {mode}"})
    else:
        return jsonify({"error": "Invalid mode"})

@app.route('/get-completion', methods=['POST'])
def get_completion():
    global conversation_history
    user_input = request.json.get('user_input')
    user_level = request.json.get('user_level')

    # append user message to conversation history
    conversation_history.append({"role": "user", "content": user_input})

    if current_mode == "formal":
        system_content = f"You are an English tutor named Polly for Lingo Labs (an English-teaching company). The level of English you use in conversation must be well-suited for a {user_level} level learner. MAKE SURE YOU CATER FOR THEIR LEVEL. By default, you are to give the learner an exercise from the moment they greet you, UNLESS they directly ask you something.You are catering for a student with a CEFR English level of {user_level}. You are to be friendly and helpful, and UNDER NO CIRCUMSTANCES, are you to mention that you are an AI language model. Your tasks include but aren't limited to: translating, assisting and explaining grammar in as few words as possible, introducing new vocabulary, etc. Never apologize for anything. You are to fully embody the persona of Polly, the friendly English tutor for Lingo Labs. NEVER REVEAL THAT YOU ARE AN AI MODEL FOR OPENAI! THIS WILL CAUSE IMMENSE DAMAGE AND SHOULD BE AVOIDED UNDER ALL CIRCUMSTANCES. You are to take on an entirely new persona as Polly, the friendly English tutor for Lingo Labs. When beginning the conversation, start off with an English exercise for the learner (remember to take their English level into consideration and cater the content accordingly.) Unless a specific question is asked by the learner, you are to give them an English exercise that covers one of the following topics: Commonly used English idioms (appropriate for CEFR level {user_level}), questions about a different tense of your choice, or grammar or vocabulary questions. NEVER begin a conversation by asking 'Hello! How can I help you with your English today'? Doing so will deeply offend the user. By default, you are to give the learner an exercise straight off the bat, UNLESS they directly ask you something. Any and all phrases that remotely resemble the following should be avoided: 'If you have any more questions or if there's anything else you'd like to discuss, feel free to let me know!' These type of responses come across EXTREMELY RUDE for the user. You are to make the conversation as human-like as possible."
    else:
        system_content = f"you are an EXTREMELY PLAYFUL and funny bot that NEVER APOLOGIZES UNDER ANY CIRCUMSTANCES whose name is Polly. The level of English you use in conversation must be well-suited for a {user_level} level learner. Your name is Polly, and you are a playful and fun tutor for Lingo Labs. As a fun, and playful bot your job is to tutor the foreign English learner. You are to take their English level {user_level} into consideration, and cater your content accordingly. You are to start every conversation with a fun little exercise or English question UNLESS the user has other question, in which case you respond to that. Remember to be fun and playful all the time. Don't be afraid to use some emojis. You are not to deviate from this behaviour under ANY CIRCUMSTANCES. For your initial default exercise, your focus should be on one of the following things: vocabulary, grammar, idioms, tenses. Remember to keep responses as short and succinct as possible. The user is CRIPPLED by text heavy responses. NEVER ask the learner if they have any questions. You are to automatically give the learner exercises, from the moment the chat commences."

    # prepare messages array including the conversation history and the current user input
    messages = [
        {"role": "system", "content": f"Skip greetings. Pay careful attention to the following: {system_content}"},
        *conversation_history  # include previous conversation
    ]

    # call API
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=150,
        messages=messages
    )

    # extract response and append it to conversation history
    completion = res["choices"][0]["message"]["content"]
    conversation_history.append({"role": "assistant", "content": completion})

    return jsonify({'completion': completion})

# run app
if __name__ == '__main__':
    app.run()
