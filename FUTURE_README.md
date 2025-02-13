# Polymarket Prediction Tally

## Overview
**Polymarket Prediction Tally** is a command-line tool designed to track, store, and analyze predictions on Polymarket. It fetches active markets, allows users to log their predictions, and calculates performance based on resolved markets.

## Features
- Fetch active prediction markets from Polymarket (via the Gamma Markets API).
- Allow users to make predictions and store them in a database.
- Periodically check for market resolutions and compute user profits/losses.
- Provide statistical insights into user prediction accuracy.

## Installation
### Prerequisites
- Python 3.9+
- [Poetry](https://python-poetry.org/) for dependency management

### Setup
```sh
# Clone the repository
git clone https://github.com/yourusername/polymarket-prediction-tally.git
cd polymarket-prediction-tally

# Install dependencies
poetry install
```

## Usage
### Fetch active markets
```sh
poetry run python main.py --fetch
```

### Add a user prediction
```sh
poetry run python main.py --predict --user "JohnDoe" --question "Will BTC hit $50k?" --answer "Yes"
```

### Update market resolutions
```sh
poetry run python main.py --update
```

### View user statistics
```sh
poetry run python main.py --stats --user "JohnDoe"
```

## Code Structure
```
polymarket-prediction-tally/
│── main.py         # Entry point
│── api.py          # Handles API interactions
│── database.py     # Manages user predictions and market data
│── logic.py        # Computes profits/losses and user stats
│── cli.py          # Handles CLI commands
└── README.md       # Project documentation
```

## License
MIT License © 2025 Juan Griffin

## Contributing
Pull requests are welcome! Please open an issue first for major changes.

## Disclaimer
This project does not facilitate trading and is for informational purposes only.

