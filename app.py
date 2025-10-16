from flask import Flask, render_template, request, redirect, url_for, stream_with_context, abort, Response
import requests
import urllib.parse

app = Flask(__name__)

ALLOWED_HOSTS = {
    "api.nasa.gov",
    "mars.nasa.gov",
    "images-assets.nasa.gov",
    "cdn.pixabay.com"
}
    
@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/submit', methods=['POST'])
def submit():
    rover = request.form.get('rover')
    date = request.form.get('date')
    mode = request.form.get('mode')
     
    print(mode)
    if not rover:
        return render_template('index.html', error="Please select a rover.")
    
    if mode == 'latest':
        return redirect(url_for('latest', rover=rover, mode=mode))
    else:
        if not date:
            return render_template('index.html', error="Please select a date.")
        return redirect(url_for('result', rover=rover, date=date, mode=mode))

@app.route('/result')
def result():
    rover = request.args.get('rover')
    date = request.args.get('date')
    mode = request.args.get('mode')
    data = requests.get(f'https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?api_key=nqAad1Z7Jg9OrH3UXdYhpfaKGGePBckgUxJV508d&earth_date={date}').json()
    # explicit API key lmao
    
    photos = data.get('photos', [])
    return render_template('index.html', photos=photos, rover=rover, date=date, mode=mode)

@app.route('/latest')
def latest():
    rover = request.args.get('rover')
    mode = request.args.get('mode')

    data = requests.get(f'https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/latest_photos?api_key=nqAad1Z7Jg9OrH3UXdYhpfaKGGePBckgUxJV508d').json()

    photos = data.get('latest_photos', [])
    return render_template('index.html', photos=photos, rover=rover, mode=mode)

def host_allowed(url):
    try:
        host = urllib.parse.urlparse(url).hostname or ""
        return any(host.endswith(a) for a in ALLOWED_HOSTS)
    except Exception:
        return False
    
# chatgpt
@app.route('/download')
def download_proxy():
    url = request.args.get('url')
    filename = request.args.get('filename', 'image.jpg')

    if not url:
        abort(400, "Missing 'url' parameter.")
    if not host_allowed(url):
        abort(403, "Host not allowed.")

    try:
        r = requests.get(url, stream=True, timeout=15)
    except Exception as e:
        abort(502, f"Error fetching image: {e}")

    if r.status_code != 200:
        abort(r.status_code)

    content_type = r.headers.get('Content-Type', 'application/octet-stream')
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}

    return Response(stream_with_context(r.iter_content(8192)), headers=headers, content_type=content_type)

if __name__ == '__main__':
    app.run(debug=True)