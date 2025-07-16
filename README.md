# Analytics Agent CLI

An analytics agent that understands plain English, analyzes your real data locally, and integrates directly into your existing workflow.

## The Problem

Every data analyst knows this workflow:

1. Export data from your system
2. Upload to ChatGPT or Claude
3. Get analysis suggestions
4. Manually implement the code
5. Debug, iterate, visualize
6. Copy results back to your report

**Analytics Agent CLI eliminates these manual steps** by creating an AI agent that actually performs the analysis in your local environment.

## What This Does

```bash
$ cd sample_data
$ aacli "What drives order value in this dataset? Show me the relationships."

-> Loading ecommerce_orders.json...
-> Analyzing correlations between order_value and other variables...
-> Found strong correlation (0.84) with customer_lifetime_value
-> Creating visualization...
✓ Chart saved: outputs/charts/order_drivers_analysis.html

$ aacli "Create a report summarizing key insights"

-> Generating comprehensive analysis...
✓ Report exported: outputs/reports/insights_orders.html
```

**Real outputs from actual execution** - not suggestions or code snippets.

**Generated Chart:**

<img src="assets/sample-chart.png" alt="Analytics Chart" width="600">

**Generated Report:**

<img src="assets/sample-report.png" alt="Insights Report" width="500">

## How It Works

The AI agent (powered by Google Gemini) translates natural language requests into function calls:

- **Function Calling**: Gemini maps user requests to appropriate functions from 57 available operations
- **Data Operations**: Load datasets (CSV/JSON), perform statistical analysis, create visualizations
- **Session Memory**: Loaded datasets persist across conversation turns in the working directory
- **File Validation**: Checks file paths and permissions before operations
- **Structured Outputs**: Returns analysis results, charts (HTML), and reports in organized formats

## Key Capabilities

### Data Analysis Functions (36 operations)

- **Load & Manage Data**: Import CSV/JSON files, list loaded datasets, merge multiple sources
- **Statistical Analysis**: Find correlations, detect outliers, calculate feature importance
- **Visualizations**: Create charts (bar, scatter, line, histogram), generate dashboards
- **Segmentation**: Group data by categories, analyze distributions, time series analysis
- **Quality Checks**: Validate data quality, identify missing values, memory optimization
- **Custom Analysis**: Execute Python code against datasets in sandboxed environment

### Excel Automation (16 operations)

- **Workbook Management**: Create/open workbooks, add worksheets, read/write data
- **Formatting**: Apply cell styles, create formulas, manage ranges
- **Advanced Features**: Create pivot tables, charts within Excel, conditional formatting

### Intelligent Guidance (9 prompts)

- **Adaptive Assistance**: Get analysis suggestions based on your dataset structure
- **Workflow Guidance**: Step-by-step help for correlations, segmentation, quality assessment
- **Audience-Specific**: Dashboard design for executives vs analysts vs operational teams
- **Discovery Support**: Find available data sources, explore patterns systematically

### File Operations (5 operations)

- **Safe Access**: Read/write files with path validation
- **Code Execution**: Run Python scripts with timeout protection
- **Content Discovery**: List files in directories with pattern matching

## 🏗️ Project Architecture

```
analytic-agent-cli/
├── staffer/                    # Core agent engine
│   ├── functions/             # Function implementations
│   │   ├── analytics/         # 36 analytics functions (tools/resources/prompts)
│   │   ├── excel/            # 16 Excel automation functions  
│   │   └── file_ops/         # 5 file system operations
│   ├── function_registries/   # Dynamic function discovery & registration
│   ├── cli/                  # Command line interface
│   └── available_functions.py # LLM integration & monitoring layer
└── sample_data/              # Example datasets for testing
```

**Key Design Decisions:**

- Type-safe function orchestration prevents runtime errors
- Smart serialization handles complex data structures
- Defensive programming ensures graceful error handling
- Session persistence maintains analytical context

**[→ Read the detailed Technical Architecture](docs/ARCHITECTURE.md)**

## Quick Start

```bash
# Install
git clone https://github.com/FT1006/analytic-agent-cli.git
cd analytic-agent-cli
pip install -e .

# Setup API Key (Free from Google AI Studio)
export GEMINI_API_KEY=your_key_here

# Try it
cd examples/ecommerce_analytics
aacli
```

## Example Use Cases

**Data Quality Assessment:**

```
> Check for data quality issues and suggest fixes
```

**Business Analysis:**

```
> Segment customers by purchase behavior and visualize the differences  
```

**Statistical Investigation:**

```
> Find factors that correlate with customer churn
```

**Report Generation:**

```
> Create an executive summary with key metrics and trends
```

## Requirements

* Python 3.10+
* Google Gemini API key (free tier available)
* Optional enhancements: pandas, openpyxl

**Note**: Currently supports Google Gemini API only.
