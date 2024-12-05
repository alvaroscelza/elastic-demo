import os

from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from flask import Flask, request, jsonify

app = Flask(__name__)


load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")


@app.route('/', methods=['GET'])
def process_urls():
    firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    booking_url = request.args.get('booking_url')
    booking_data = firecrawl_app.crawl_url(
        booking_url,
        params={
            'limit': 100,
            'scrapeOptions': {'formats': ['markdown', 'html']}
        },
        poll_interval=30
    )

    website_url = request.args.get('website_url')
    website_data = firecrawl_app.crawl_url(
        website_url,
        params={
            'limit': 100,
            'scrapeOptions': {'formats': ['markdown', 'html']}
        },
        poll_interval=30
    )

    # Return the URLs in the response
    return jsonify({
        "booking_data": booking_data,
        "website_data": website_data
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
