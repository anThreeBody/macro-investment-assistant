# 📊 Macro Investment Assistant

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**AI-Powered Macro Investment Analysis Platform**

An intelligent investment decision support system based on multi-factor models and macro narrative analysis, providing daily investment briefs, market sentiment analysis, and prediction verification.

---

## 🌟 Features

### Core Capabilities

- 📈 **Multi-Factor Prediction Model** - Integrates macroeconomics, market sentiment, capital flows, and more
- 📰 **Macro Narrative Analysis** - Automatically identifies policy types and derives asset price implications
- 📊 **Daily Investment Brief** - Comprehensive reports including gold prices, funds, stocks, and news
- 🔍 **Prediction Verification** - Continuous tracking with 7/30/90-day accuracy statistics
- 😱 **Fear & Greed Index** - 5-indicator weighted market sentiment composite
- 📅 **Event Calendar** - Important economic events for the next 7 days
- 🤖 **RESTful API** - Full API support for third-party integration

### Data Sources

| Category | Sources | Update Frequency |
|----------|---------|------------------|
| Gold Prices | East Money, Jin10 | Real-time |
| Fund NAV | AKShare | Daily |
| Stock Market | East Money | Real-time |
| News | Tencent, Baidu, Sina, East Money, Hexun | Hourly |
| Macro Data | Federal Reserve, NBS | As released |

---

## 🚀 Quick Start

### Requirements

- Python 3.9+
- macOS / Linux / Windows
- Internet access (for real-time data)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/anThreeBody/macro-investment-assistant.git
cd macro-investment-assistant

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. Test installation
python3 main.py --help
```

### Generate Daily Brief

```bash
# One-click daily brief generation
./run_daily.sh

# Or run manually
python3 main.py brief
```

### Start API Server

```bash
# Start API service
./api/start.sh

# Access API docs
open http://localhost:8000/docs
```

---

## 📁 Project Structure

```
macro-investment-assistant/
├── main.py                 # Main entry point
├── run_daily.sh           # Daily execution script
├── requirements.txt       # Python dependencies
├── config.yaml           # Configuration file
│
├── analyzers/            # Analysis modules
│   ├── macro.py          # Macro analysis
│   ├── macro_narrative.py # Macro narrative analysis
│   ├── fear_greed_index.py # Fear & Greed Index
│   └── ...
│
├── data_sources/         # Data source modules
│   ├── gold_source.py    # Gold price data
│   ├── fund_source.py    # Fund data
│   ├── news_source.py    # News data
│   └── ...
│
├── predictors/           # Prediction modules
│   ├── multi_factor.py   # Multi-factor prediction
│   ├── validator.py      # Prediction validation
│   └── ...
│
├── presenters/           # Presentation modules
│   ├── brief_generator_enhanced.py # Brief generation
│   └── ...
│
├── api/                  # API service
│   ├── main.py          # FastAPI application
│   └── ...
│
├── web/                  # Web dashboard
│   └── dashboard.html
│
├── docs/                 # Documentation
│   ├── INDEX.md         # Documentation index
│   ├── CHANGELOG.md     # Changelog
│   └── ...
│
└── tests/               # Test cases
```

---

## 📊 System Version

**Current Version**: V8.4.5 (2026-04-15)

### Latest Changes

#### V8.4.5 - Prediction Logic Optimization

**Key Changes**:
- ✅ Removed sideways prediction, only up/down directions
- ✅ Direction threshold adjusted from ±1% to ±0.5%
- ✅ Prediction interval reduced from ±2% to ±1%
- ✅ Smart fund NAV column detection
- ✅ Real-time northbound capital flow (no longer hardcoded)

**Impact**:
```
Direction: Up/Down/Sideways → Up/Down (clearer)
Interval: ±2% (4.2% span) → ±1% (2.0% span) (more precise)
Fund NAV: Multiple 0.0 → All valid (more reliable)
Northbound: Fixed 35.8B → Real-time fetch (more accurate)
```

[View Full Version History →](docs/VERSION_HISTORY.md)

---

## 🔧 Usage Guide

### Command Line Interface

```bash
# View help
python3 main.py --help

# Generate daily brief
python3 main.py brief

# Get gold prices
python3 main.py gold

# Generate prediction
python3 main.py predict

# Verify predictions
python3 main.py verify

# Start API server
python3 main.py api
```

### Configuration

Edit `config.yaml`:

```yaml
# Data source configuration
data_sources:
  gold:
    primary: "eastmoney"
    fallback: "jin10"
  
  news:
    sources:
      - "tencent"
      - "baidu"
      - "sina"
      - "eastmoney"
      - "hexun"

# Prediction configuration
prediction:
  direction_threshold: 0.005  # ±0.5%
  prediction_interval: 0.01   # ±1%
  
# Alert configuration
alerts:
  enabled: true
  price_change_threshold: 2.0  # 2%
```

---

## 📈 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface Layer                  │
│  CLI  │  Web Dashboard  │  API  │  Daily Brief          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Business Logic Layer                  │
│  Prediction Engine  │  Analyzers  │  Validator  │  Alerts│
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Data Source Layer                     │
│  Gold  │  Funds  │  Stocks  │  News  │  Macro Data      │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Data Storage Layer                    │
│  SQLite  │  JSON Cache  │  Logs                         │
└─────────────────────────────────────────────────────────┘
```

[View Full Architecture →](docs/ARCHITECTURE.md)

---

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest tests/

# Run specific test
python3 -m pytest tests/test_gold_source.py

# Generate coverage report
python3 -m pytest --cov=. tests/
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Quick start (English) |
| [README_ZH.md](README_ZH.md) | 快速开始（中文） |
| [docs/INDEX.md](docs/INDEX.md) | Complete documentation index |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Changelog |
| [docs/VERSION_HISTORY.md](docs/VERSION_HISTORY.md) | Version history |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [api/API_GUIDE.md](api/API_GUIDE.md) | API documentation |

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get involved.

### Contributors

<!-- readme: contributors -start -->
<!-- readme: contributors -end -->

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

- 📧 Email: [Coming soon]
- 💬 Issues: [GitHub Issues](https://github.com/anThreeBody/macro-investment-assistant/issues)
- 📖 Wiki: [Project Wiki](https://github.com/anThreeBody/macro-investment-assistant/wiki)

---

## 🙏 Acknowledgments

Thanks to these open source projects:

- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [Playwright](https://playwright.dev/) - Browser automation
- [AKShare](https://akshare.akfamily.xyz/) - Financial data API
- [Matplotlib](https://matplotlib.org/) - Chart generation

---

<div align="center">

**If you find this project helpful, please give it a ⭐ Star!**

[↑ Back to top](#-macro-investment-assistant)

</div>
