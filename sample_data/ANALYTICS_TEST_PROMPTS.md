# Analytics Test Prompts for Analytics Agent CLI

This document contains a comprehensive set of test prompts designed to validate and showcase the analytics capabilities of the Analytics Agent CLI. These prompts are organized by difficulty level and test various aspects of the system.

## Available Test Datasets

Located in `sample_data/`:
- **ecommerce_orders.json** - E-commerce transaction data (15 orders)
- **employee_survey.csv** - Employee satisfaction and workforce data (25 employees)
- **product_performance.csv** - Product sales and inventory metrics (20 products)

## Beginner Level Tests

### 1. Data Loading & First Look
```
Load the e-commerce dataset and give me a first look at the data structure
```
**Tests**: Basic data loading, schema discovery, initial exploration

### 2. Simple Visualization
```
Create a bar chart showing order values by product category using the e-commerce data
```
**Tests**: Basic chart creation, single dataset visualization

### 3. Basic Data Quality Check
```
Run a data quality assessment on the employee survey dataset
```
**Tests**: Data quality validation, missing value detection

## Intermediate Level Tests

### 4. Multi-Dataset Analysis
```
Load all three datasets (ecommerce_orders.json, employee_survey.csv, product_performance.csv) and compare their data quality scores
```
**Tests**: Multiple dataset handling, comparative analysis

### 5. Correlation Discovery
```
Find correlations in the employee data and create a scatter plot of the strongest relationship
```
**Tests**: Statistical analysis, automatic insight discovery, correlation visualization

### 6. Segmentation Analysis
```
Segment the e-commerce orders by region and show me which region has the highest average order value
```
**Tests**: Categorical segmentation, aggregation calculations

### 7. Time Series Analysis
```
Analyze order trends over time using the e-commerce data and identify any seasonal patterns
```
**Tests**: Temporal analysis, trend detection, pattern recognition

## Advanced Level Tests

### 8. Comprehensive Dashboard Creation
```
Create a complete analysis dashboard for the product performance data including distributions, correlations, and segmentation by category
```
**Tests**: Multi-visualization dashboard, comprehensive analysis workflow

### 9. Cross-Dataset Insights
```
Load both the e-commerce and product performance datasets, then find insights about how product categories perform across both datasets
```
**Tests**: Dataset merging, cross-dataset analysis, insight generation

### 10. Data Quality + Visualization Pipeline
```
Validate data quality for all three datasets, then create the most insightful visualization for each based on their characteristics
```
**Tests**: Automated analysis selection, data-driven visualization choices

## Creative Problem-Solving Tests

### 11. Business Intelligence Scenario
```
Act as a business analyst and provide actionable insights from the e-commerce data that could help improve sales performance
```
**Tests**: Business context understanding, actionable recommendations, strategic analysis

### 12. HR Analytics Challenge
```
Using the employee survey data, identify potential retention risks and suggest data-driven recommendations
```
**Tests**: HR analytics, risk identification, predictive insights

### 13. Product Portfolio Analysis
```
Analyze the product performance data to recommend which products to promote, discontinue, or reorder based on the available metrics
```
**Tests**: Portfolio optimization, multi-metric decision making

## Stress Tests

### 14. Complex Multi-Step Analysis
```
Load the e-commerce data, perform outlier detection on order values, create distribution analysis, segment by customer type, and export all insights to a comprehensive report
```
**Tests**: Complex workflow execution, multiple function integration, report generation

### 15. Analytics Function Showcase
```
Demonstrate as many different analytics capabilities as possible using the employee survey dataset - show me what this system can do
```
**Tests**: Full capability demonstration, function discovery, system limits

## Test Coverage Matrix

| Prompt # | Loading | Visualization | Statistics | Quality Check | Multi-Dataset | Export | AI Reasoning |
|----------|---------|---------------|------------|---------------|---------------|---------|--------------|
| 1        | ✓       |               |            |               |               |         | ✓            |
| 2        | ✓       | ✓             |            |               |               |         | ✓            |
| 3        | ✓       |               |            | ✓             |               |         | ✓            |
| 4        | ✓       |               |            | ✓             | ✓             |         | ✓            |
| 5        | ✓       | ✓             | ✓          |               |               |         | ✓            |
| 6        | ✓       |               | ✓          |               |               |         | ✓            |
| 7        | ✓       | ✓             | ✓          |               |               |         | ✓            |
| 8        | ✓       | ✓             | ✓          |               |               |         | ✓            |
| 9        | ✓       | ✓             | ✓          |               | ✓             |         | ✓            |
| 10       | ✓       | ✓             |            | ✓             | ✓             |         | ✓            |
| 11       | ✓       | ✓             | ✓          |               |               |         | ✓            |
| 12       | ✓       | ✓             | ✓          |               |               |         | ✓            |
| 13       | ✓       | ✓             | ✓          |               |               |         | ✓            |
| 14       | ✓       | ✓             | ✓          | ✓             |               | ✓       | ✓            |
| 15       | ✓       | ✓             | ✓          | ✓             |               | ✓       | ✓            |

## Expected Outcomes

These prompts test:
- **Function Integration**: Loading → Analysis → Visualization workflows
- **Multi-Dataset Handling**: Managing multiple datasets simultaneously
- **Analytics Variety**: Different chart types and statistical functions
- **Business Context**: Understanding and providing actionable insights
- **Error Handling**: Graceful handling of edge cases and data issues
- **Complex Workflows**: Multi-step analyses with dependencies
- **AI Reasoning**: Appropriate analysis selection and interpretation

## Usage Instructions

1. Navigate to the sample data directory:
   ```bash
   cd sample_data
   ```

2. Start Analytics Agent CLI:
   ```bash
   aacli
   ```

3. Copy and paste any prompt from this document

4. Observe the system's response and verify expected functionality

## Common Issues to Watch For

- JSON serialization errors (should be fixed)
- Function name confusion (create_chart_excel vs create_analytic_chart_html)
- Session restoration errors (should be fixed)
- Dataset not found errors (ensure correct file paths)
- Memory issues with large datasets

## Notes

- All prompts assume you're in the `sample_data` directory
- Dataset files should be referenced with relative paths (e.g., `./employee_survey.csv`)
- Some prompts may require multiple steps - the AI should handle this automatically
- Results may vary based on the AI's interpretation and decision-making