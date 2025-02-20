# Polymarket Prediction Tally

## Overview
**Polymarket Prediction Tally** is a command-line tool designed to track, store, and analyze predictions on Polymarket. It fetches active markets, allows users to log their predictions, and calculates performance based on resolved markets.

## Features
- Fetch active prediction markets from Polymarket (via the [Gamma Markets API][https://docs.polymarket.com/#gamma-markets-api]).
- Allow users to make predictions and store them in a database.
- Periodically check for market resolutions and update prediction statistics.
- Provide statistical insights into user prediction accuracy.

## Installation

### Prerequisites
- Python 3.10+
- [Poetry](https://python-poetry.org/) (for dependency management)

### Steps
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
2. Install dependencies with Poetry:
    ```bash
    poetry install
    ```
3. Build the package:
    ```bash
    poetry build
    ```
4. Install the built package:
```bash
pip install dist/polymarket_predictions_tally-0.1.0-py3-none-any.whl
```

## Usage
After installation, you can use the `polytally` command from anywhere in your terminal. Below are the available commands and their purposes:

- **Make predictions for a user**  
    ```bash
    polytally predict [username]
    ```
    Replace `[username]` with the desired username. If the user does not exist, they will be created automatically.
- **View prediction history for a user**
    ```bash
    polytally history [username]
    ```
    Displays all past predictions made by the specified user, including outcomes and performance metrics.
- **Update predictions and statistics**
    ```bash
    polytally update
    ```
    Checks for newly resolved markets and updates user profits, losses, and prediction accuracy based on the latest data.
- **View help information**
    ```bash
    polytally -h
    ```
    Shows all available commands and usage options.
## License
MIT License © 2025 Juan Griffin

## Contributing
Pull requests are welcome! Please open an issue first for major changes.

## Disclaimer
This project does not facilitate trading and is for informational purposes only.
