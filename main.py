import os

from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)


load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")


@app.route('/', methods=['GET'])
def process_urls():
    firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    openai_client = OpenAI(api_key=OPEN_AI_API_KEY)

    booking_url = request.args.get('booking_url')
    booking_data = firecrawl_app.crawl_url(
        booking_url,
        params={
            'limit': 100,
            'scrapeOptions': {'formats': ['markdown']}
        },
        poll_interval=30
    )
    booking_data = booking_data['data'][0]['markdown']
    init_index = booking_data.find('*\n\n## Availability\n\nWe')
    end_index = booking_data.find('Guest reviews')
    booking_data = booking_data[init_index:end_index]
    prompt =f"I'll give you a markdown content. Extract room type rates information. Add details of each room so I can differentiate the different options. Return the response in Json format in a structured way. Ensure that you return rate: {booking_data}"
    booking_analysis = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            n=1,
            temperature=0.7,
        )
    booking_analysis = booking_analysis.choices[0].message.content

    # website_url = 'https://be.bookingexpert.it/book/simple/step2?checkin=1736722800000&checkout=1736809200000&hotel=42803&guesttypes[0][18299]=1&ages[0][18299]=18&layout=13902&lang=it&currency=EUR&_ga=2.49309793.656897126.1733405737-880813913.1733405737&nsid=a9c102ea-5269-45cf-9559-d7a04741c751&winding=1&searchId=0a078d9e-a4a7-46b0-b3ad-b22ee9d490e3'
    # website_data = firecrawl_app.crawl_url(
    #     website_url,
    #     params={
    #         'limit': 100,
    #         'scrapeOptions': {'formats': ['markdown']}
    #     },
    #     poll_interval=30
    # )

    # Return the URLs in the response
    return jsonify({
        "booking_data": booking_analysis
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
