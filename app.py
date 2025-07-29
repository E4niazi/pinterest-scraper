from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['POST'])
def scrape_pinterest():
    data = request.get_json()
    pinterest_url = data.get('url')

    if not pinterest_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(pinterest_url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and 'contentUrl' in script.string:
                match = re.search(r'"contentUrl":"(.*?)"', script.string)
                if match:
                    media_url = match.group(1).replace("\\u002F", "/")
                    media_type = 'video' if media_url.endswith('.mp4') else 'image'
                    return jsonify({'media_url': media_url, 'media_type': media_type})

        return jsonify({'error': 'Media not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
