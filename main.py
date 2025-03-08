from flask import Flask
from flask import render_template , request , url_for
from dotenv import load_dotenv
import os
import requests
from webhook_sender   import send_to_discord

load_dotenv()

CLOUDFLARE_API_TOKEN=os.getenv("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_API_ID=os.getenv("CLOUDFLARE_API_ID")
DISCORD_WEBHOOK_URL=os.getenv("DISCORD_WEBHOOK_URL")

app = Flask(__name__)

def generate_image(prompt, num):
    API_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_API_ID}/ai/run/"
    module = "@cf/lykon/dreamshaper-8-lcm"
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    data = { "prompt" : prompt}
    if (num == 2):
        data = { "prompt" : prompt + " image"}


    response = requests.post(f"{API_BASE_URL}{module}" , headers=headers, json=data )
    print( response.status_code )
    if(response.status_code == 200 and response.headers["Content-Type"] == "image/png"):
        image_path = os.path.join("static", str(num) + "generated.png")
        print (image_path)
        with open(image_path, "wb") as f:
            f.write(response.content)
        url = url_for("static", filename= str(num) + "generated.png")
    else:
        print( response.text)
        url = url_for("static", filename="fail.jpg")
    return url

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/generate_card", methods=["POST"])
def generate_card():
    prompt = request.form["prompt"]
    message = request.form["message"]
    print (prompt, message)
    image_url = generate_image(prompt, 1)
    image_url2 = generate_image(prompt, 2)
    return render_template("card.html", prompt=prompt, text=message, image_url=image_url, image_url2=image_url2)      


@app.route("/send_webhook", methods=["POST"])
def send_webhook():
    image_url = request.form["image_url"]
    text = request.form["text"]
    url = request.form["url"]
    number = request.form["number"]
    if text and image_url:
        image_path = os.path.join("static", number + "generated.png")
        send_to_discord(image_path, text, url)
    else:
        image_path = os.path.join("static", "fail.jpg")
    return render_template("discord_response.html")

if __name__ == "__main__":
    app.run(debug=True)
