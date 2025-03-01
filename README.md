# BestBuy Bot

A real-time automation tool for monitoring and purchasing products from Best Buy. The bot checks product availability, adds items to the cart, and notifies you via email when the product is in stock.

## Features

- Scans specified Best Buy product page
- Clicks "Add To Cart" and proceeds to checkout
- Sends email notifications on start, product add, and shutdown
- Configurable test and headless modes for debugging and production use

## Prerequisites

- Python 3.9+
- Firefox installed (with a compatible profile)
- Required Python packages (see `requirements.txt`)
- Environment variables set for:
	- `BESTBUY_URL`
	- `EMAIL_FROM`
	- `EMAIL_TO`
	- `SMTP_SERVER`
	- `SMTP_PORT`
	- `EMAIL_PASSWORD`

## Installation

1. Clone the repository.
2. Install the dependencies:
	 ```
	 pip install -r requirements.txt
	 ```

## Usage

1. Configure your environment variables.
2. Run the bot:
	 ```
	 python bestbuy.py
	 ```

## Docker Deployment

Build and run the bot using Docker with the provided `Dockerfile` and `docker-compose.yaml`.

To run with Docker Compose:
```
docker-compose up -d
```

Ensure you update the environment variables in the `docker-compose.yaml` file before deployment.

## Configuration

- **Product URL**: Set the target product URL via the `BESTBUY_URL` environment variable.
- **Email Notifications**: Configure the email sender, recipient, SMTP server, port, and password.
- **Test Mode**: When testing, set `test_mode` to `True` to avoid processing an actual purchase.
- **Headless Mode**: Enable `headless_mode` for background execution.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is provided as-is without any warranty.
