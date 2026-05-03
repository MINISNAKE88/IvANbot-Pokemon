from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    # This message will appear when you visit the bot's web URL
    return "Bot is active and running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # This creates a separate thread so the web server runs 
    # alongside the bot without blocking it
    t = Thread(target=run)
    t.start()
