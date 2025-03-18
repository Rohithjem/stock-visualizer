import matplotlib.pyplot as plt
import time
import boto3
import yfinance as yf

AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
BUCKET_NAME = "my-stock-charts"

STOCK_SYMBOLS = ["AAPL", "MSFT", "TSLA", "AMZN", "GOOGL"]
COLORS = ["blue", "green", "red", "purple", "orange"]  

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name="us-east-1"
)

timestamps = []
prices_dict = {symbol: [] for symbol in STOCK_SYMBOLS}

def upload_to_s3(file_name):
    """Upload file to S3 bucket with correct Content-Type"""
    s3.upload_file(
        file_name,
        BUCKET_NAME,
        file_name,
        ExtraArgs={"ContentType": "image/png"}
    )
    print(f"Uploaded {file_name} to S3: https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}")

def fetch_and_plot():
    """Fetch stock prices for multiple companies and update the line chart"""
    global timestamps
    current_time = time.strftime("%H:%M:%S")  
    timestamps.append(current_time)

    for stock in STOCK_SYMBOLS:
        try:
            stock_data = yf.Ticker(stock)
            price = stock_data.fast_info["last_price"]  
            prices_dict[stock].append(price)
        except Exception as e:
            print(f"Error fetching {stock}: {e}")
            prices_dict[stock].append(None)  


        if len(timestamps) > 10:
            timestamps.pop(0)
            for key in prices_dict:
                prices_dict[key].pop(0)

    plt.clf()
    for stock, color in zip(STOCK_SYMBOLS, COLORS):
        plt.plot(timestamps, prices_dict[stock], marker="o", linestyle="-", color=color, label=stock)

    plt.xlabel("Time")
    plt.ylabel("Stock Price (USD)")
    plt.title("Live Stock Prices for 5 Companies")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()


    chart_filename = "stock_chart.png"
    plt.savefig(chart_filename)
    upload_to_s3(chart_filename)

    plt.pause(10)  

plt.ion()
plt.figure()

while True:
    fetch_and_plot()
