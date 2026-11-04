import os
from anthropic import Anthropic

# The client will automatically read the ANTHROPIC_API_KEY environment variable
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-sonnet-5-5", # You can choose the appropriate model based on your needs
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)
print(message.content[0].text)
conversation = []
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    conversation.append({"role": "user", "content": user_input})
    
    message = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        messages=conversation # Pass the complete history
    )
    reply = message.content[0].text
    print(f"Claude: {reply}")
    conversation.append({"role": "assistant", "content": reply})
    message = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    system="You are a helpful assistant who answers questions concisely.",
    messages=[{"role": "user", "content": "Introduce yourself"}]
    )
