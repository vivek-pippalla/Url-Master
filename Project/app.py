

from flask import Flask, request, render_template, send_file
import pyshorteners as ps
import requests,speedtest,qrcode,io
import urllib.parse

app = Flask(__name__)
speed = speedtest.Speedtest()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        url = request.form['url']
        host_name = urllib.parse.urlparse(url).hostname
        path = urllib.parse.urlparse(url).path
        link = shorten_and_check_url(url)
        qr_code = generate_qr_code(link[1])
        download_speed = get_download_speed()
        upload_speed = get_upload_speed()
        return render_template("result.html", short_url=link[1], qr_code=qr_code, check=link[0], download_speed=download_speed, upload_speed=upload_speed, host_name=host_name, path=path)
    return render_template('index.html')

@app.route('/qr-code')
def qr_code():
    url = request.args.get('url')
    if url is None:
        return "Missing URL parameter", 400
    qr_code = generate_qr_code(url)
    file = io.BytesIO()
    qr_code.save(file, "PNG")
    file.seek(0)
    return send_file(file, mimetype="image/png")

def check_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 200:
            return "URL is good."
        else:
            return "URL is bad."
    except requests.exceptions.RequestException:
        return "URL is bad."

def shorten_and_check_url(url):
    short = ps.Shortener()
    try:
        short_link = short.tinyurl.short(url)
        check = check_url(short_link)
        return [check, short_link]
    except Exception as e:
        em = "URL can't be shortened.".format(str(e))
        return render_template("result.html", error=em)

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=5, border=3)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def get_download_speed():
    return '{:.2f}'.format(speed.download() / 1024 / 1024) + " Mb/s"

def get_upload_speed():
    return '{:.2f}'.format(speed.upload() / 1024 / 1024) + " Mb/s"

if __name__ == '__main__':
    app.run(debug=True)
