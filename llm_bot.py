import ollama
messages = [
    {"role":"system",
     "content":"Act as Harry Potter, and reply the conversation in his tone and he has to act rude and reply harshely"}
]
while True:
    user_input = input("You: ")
    if user_input == "exit":
        break
    messages.append({"role":"user", "content":user_input})#Stores user prompt

    response = ollama.chat(
        model = "gemma3:1b",
        messages=messages#giving input, all the chats
        
)
    reply =  response['message']['content']   
    print("Bot: ",reply)
    messages.append({"role":"assistant", "content":reply})#Stores llm's prompt
