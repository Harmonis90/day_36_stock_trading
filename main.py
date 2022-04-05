import requests
import config
import datetime as dt
from twilio.rest import Client

current_date = dt.date.today().isoformat()
yesterday_date = (dt.date.today() - dt.timedelta(1)).isoformat()
two_days_ago_date = (dt.date.today() - dt.timedelta(2)).isoformat()

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
API_KEY = config.STOCK_API_KEY
NEWS_KEY = config.NEWS_API_KEY
INTERVAL = "15min"
FUNCTION = "TIME_SERIES_DAILY"


def get_percentage_difference(v1: float, v2: float):
    denominator = (v1 + v2) / 2
    numerator = (v1 - v2)
    fraction = (numerator / denominator)
    answer = fraction * 100
    return answer


# # STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
stock_url = f'https://www.alphavantage.co/query?function={FUNCTION}&symbol={STOCK}&apikey={API_KEY}'

request = requests.get(stock_url)
request.raise_for_status()
stock_data = request.json()


data_by_date = stock_data["Time Series (Daily)"]
recent_closing_data_list = [value for (key, value) in data_by_date.items()]
closing_data = recent_closing_data_list[0]
closing_price = closing_data["4. close"]

yesterday_closing_data = recent_closing_data_list[1]
yesterday_closing_price = yesterday_closing_data["4. close"]

closing_difference = float(closing_price) - float(yesterday_closing_price)
percentage_difference = get_percentage_difference(float(closing_price), float(yesterday_closing_price))


# # STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

news_params = {
    'qInTitle': f"{COMPANY_NAME}",
    'from': f"{two_days_ago_date}",
    'to': f"{current_date}",
    'apiKey': f"{NEWS_KEY}"

}
news_params_2 = {
    'qInTitle': f"{COMPANY_NAME}",
    'apiKey': f"{NEWS_KEY}"
}

news_request = requests.get(f"{NEWS_ENDPOINT}", params=news_params_2)
news_request.raise_for_status()
news_data = news_request.json()['articles']

recent_news_data = news_data[:3]
# recent_headlines = [recent_news_data[title_index]['title'] for title_index in range(len(recent_news_data))]
recent_headlines = [f"Headline: {article['title']}.\nContent: {article['description']}" for article in recent_news_data]


# # STEP 3: Use https://www.twilio.com
# Send a separate message with the percentage change and each article's title and description to your phone number.
emoji = ""
if percentage_difference > 5:
    if closing_difference > 0:
        emoji = "🔺"
    else:
        emoji = "🔻"

    account_sid = config.SMS_SID
    auth_token = config.SMS_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    for headline in recent_headlines:
        message_text = f"{STOCK} {emoji}{percentage_difference:.1f}%\n{headline}"
        message = client.messages.create(
            body=f"{message_text}",
            from_=f'{config.TWILIO_NUMBER}',
            to=f"{config.MY_NUMBER}"
        )




