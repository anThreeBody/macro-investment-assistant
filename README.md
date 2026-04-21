# 📊 Macro Investment Assistant

<div align="center">

**AI-Powered Macro Investment Analysis Platform for China Market**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Documentation](docs/INDEX.md) | [中文文档](README_ZH.md) | [日本語](README_JA.md) | [Русский](README_RU.md)

</div>

---

## 🎯 Project Overview

**Macro Investment Assistant** is an intelligent investment decision support system specifically optimized for the China market. It combines multi-factor models with macro narrative analysis to provide comprehensive investment insights.

### Key Highlights

- 🇨 **China-Optimized**: Designed for mainland China network environment, works with limited international connectivity
- 📈 **Multi-Factor Prediction**: Integrates macroeconomics, market sentiment, capital flows
- 📰 **Macro Narrative Analysis**: Policy → Economic Impact → Asset Price → Investment Strategy
-  **Daily Briefs**: Automated investment reports with gold, funds, stocks, news
- 🔍 **Prediction Tracking**: 7/30/90-day accuracy verification
- 🤖 **Full API**: RESTful API for third-party integration

---

## 🌍 Why This Project?

### Problem

Most investment analysis tools are designed for global markets and require unrestricted internet access. Users in mainland China face challenges:
- Limited access to international financial data APIs
- Network latency for overseas services
- Lack of China-specific market analysis

### Solution

This project is **built for China, by China**:
- ✅ **Local Data Sources**: East Money, AKShare, Tencent, Sina (all China-based)
- ✅ **Offline-First**: Works with limited international connectivity
- ✅ **China Market Focus**: A-shares, domestic gold prices, Chinese policy analysis
- ✅ **Chinese Language**: Native Chinese documentation and support

---

## 🚀 Quick Start

### Installation (5 minutes)

```bash
# Clone repository
git clone https://github.com/anThreeBody/macro-investment-assistant.git
cd macro-investment-assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install browser automation
playwright install chromium

# Test installation
python3 main.py --help
```

### Generate Daily Brief

```bash
# One-click daily brief
./run_daily.sh

# Or manually
python3 main.py brief
```

### Start API Server

```bash
./api/start.sh
# Access: http://localhost:8000/docs
```

---

## 📊 Core Features

### 1. Multi-Factor Prediction

Integrates 10+ factors across 4 dimensions:

| Dimension | Factors | Weight |
|-----------|---------|--------|
| **Macro Economy** | GDP, CPI, PMI, Interest Rates | 30% |
| **Market Sentiment** | Fear & Greed Index, VIX | 25% |
| **Capital Flow** | Northbound Capital, Fund Flows | 25% |
| **Technical** | Price Trends, Volume | 20% |

### 2. Macro Narrative Analysis

Automatic policy analysis with causal reasoning:

```
Policy Announcement
    ↓
Economic Impact Assessment
    ↓
Asset Price Implications
    ↓
Investment Strategy Recommendation
```

**Example**:
```
📰 Policy: PBOC announces RRR cut of 50bps
    ↓
💡 Impact: Increased liquidity, lower borrowing costs
    ↓
📈 Assets: Bullish for stocks, bearish for bond yields
    ↓
💼 Strategy: Overweight financials, consumer discretionary
```

### 3. Daily Investment Brief

Automated comprehensive report including:

- 📈 Market overview (Shanghai, Shenzhen, ChiNext)
- 💰 Gold prices (international & domestic)
- 📊 Fund recommendations (top picks with analysis)
- 📰 News summary (5 major China sources)
- 🔮 Market prediction (direction + confidence)
- 📅 Event calendar (next 7 days)

### 4. Prediction Verification

Transparent accuracy tracking:

| Period | Predictions | Correct | Accuracy |
|--------|-------------|---------|----------|
| **7 days** | 5 | 3 | 60% |
| **30 days** | 22 | 13 | 59% |
| **90 days** | 65 | 38 | 58% |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│  CLI  │  Web Dashboard  │  REST API  │  Daily Brief    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                 Business Logic Layer                     │
│  Prediction Engine  │  Analyzers  │  Validator  │ Alert │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Data Sources (China)                    │
│  East Money  │  AKShare  │  Tencent  │  Sina  │  Hexun │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Data Storage                          │
│  SQLite Database  │  JSON Cache  │  Local Files        │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
macro-investment-assistant/
├── 📄 Core Files
│   ├── main.py                 # Main entry point
│   ├── run_daily.sh           # Daily execution script
│   ├── requirements.txt       # Dependencies
│   └── config.yaml           # Configuration
│
├── 🧠 Analysis Modules
│   ├── analyzers/            # Analysis engines
│   │   ├── macro.py          # Macro analysis
│   │   ├── macro_narrative.py # Narrative analysis ⭐
│   │   └── fear_greed_index.py # Sentiment index
│   │
│   ├── predictors/           # Prediction models
│   │   ├── multi_factor.py   # Multi-factor prediction
│   │   └── validator.py      # Prediction validation
│   │
│   └── data_sources/         # China data sources
│       ├── gold_source.py    # Gold prices (East Money)
│       ├── fund_source.py    # Fund NAV (AKShare)
│       └── news_source.py    # News (5 China sources)
│
├── 🌐 API & Web
│   ├── api/                  # REST API (FastAPI)
│   └── web/                  # Web dashboard
│
├── 📚 Documentation
│   ├── docs/                 # Technical docs
│   ├── README.md            # This file (English)
│   └── README_ZH.md         # 中文文档
│
└── 🧪 Tests
    └── tests/               # Test cases
```

---

## 📊 Current Version

**Version**: V8.4.5 (2026-04-15)

### Latest Changes (V8.4.5)

- ✅ **Simplified Prediction**: Removed sideways, only up/down (clearer signals)
- ✅ **Tighter Threshold**: Direction ±0.5% (more sensitive)
- ✅ **Precise Interval**: Prediction ±1% (better guidance)
- ✅ **Smart Fund Data**: Auto-detect AKShare columns (weekend/holiday handling)
- ✅ **Real-time Northbound**: Dynamic API fetch (no hardcoded values)

[View Full Changelog →](docs/CHANGELOG.md)

---

## 🔧 Usage Examples

### Command Line

```bash
# Generate daily brief
python3 main.py brief

# Get latest gold prices
python3 main.py gold

# Generate prediction
python3 main.py predict

# Verify past predictions
python3 main.py verify

# Start API server
python3 main.py api
```

### Configuration

Edit `config.yaml`:

```yaml
data_sources:
  gold:
    primary: "eastmoney"    # China-based
    fallback: "jin10"       # China-based
  
  news:
    sources:
      - "tencent"           # 腾讯新闻
      - "baidu"             # 百度新闻
      - "sina"              # 新浪财经
      - "eastmoney"         # 东方财富
      - "hexun"             # 和讯网

prediction:
  direction_threshold: 0.005  # ±0.5%
  prediction_interval: 0.01   # ±1%
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📖 Documentation Index](docs/INDEX.md) | Complete docs |
| [📝 Changelog](docs/CHANGELOG.md) | Version history |
| [🏗️ Architecture](docs/ARCHITECTURE.md) | System design |
| [📊 Version History](docs/VERSION_HISTORY.md) | All versions |
| [🤝 Contributing](CONTRIBUTING.md) | How to contribute |
| [🌐 API Guide](api/API_GUIDE.md) | API documentation |

**Language Versions**:
- [🇬🇧 English](README.md) - You are here
- [🇨🇳 中文](README_ZH.md) - 中文版
- [🇯🇵 日本語](README_JA.md) - Coming soon
- [🇷🇺 Русский](README_RU.md) - Coming soon

---

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest tests/

# With coverage
python3 -m pytest --cov=. tests/

# Specific test
python3 -m pytest tests/test_gold_source.py
```

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How to Help

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🌍 Translate to your language
- 💻 Submit pull requests

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with these amazing open-source projects:

- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [Playwright](https://playwright.dev/) - Browser automation
- [AKShare](https://akshare.akfamily.xyz/) - China financial data
- [Matplotlib](https://matplotlib.org/) - Charting

---

<div align="center">

**If you find this project useful, please give it a ⭐ Star!**

Made with ❤️ for the China investment community

[↑ Back to top](#-macro-investment-assistant)

</div>
