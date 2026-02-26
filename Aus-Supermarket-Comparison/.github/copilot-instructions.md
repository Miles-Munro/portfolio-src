# Copilot Instructions - Aus Supermarket Comparison

## Project Overview
This project tracks and compares product prices across Australian supermarket chains (Coles, Aldi, etc.) over time to identify price trends and comparison opportunities.

## Data Architecture

### Core Data Format
- **Source**: External scraper (`grocery-scraper` GitHub project) provides raw product data
- **Storage**: `cleanProductInfo.json` - array of product objects with nested price history
- **Schema** (each product):
  ```json
  {
    "name": "Product Name",
    "url": "https://supermarket.com.au/product/...",
    "img": "https://cdn.../image.jpg",
    "quantity": <number>,
    "history": [
      {"daySinceEpoch": <days>, "price": <AUD>}
    ]
  }
  ```

### Key Data Patterns
- **Price History**: Use `daySinceEpoch` for temporal comparisons, not absolute dates (enables time-based analysis)
- **Multi-chain Data**: Products are mixed sources (Coles, Aldi URLs); preserve source URL for chain attribution
- **Quantity Variance**: Same product may have different quantities; include in comparison logic

## Development Workflow

### Data Processing Pipeline
1. Load JSON: `clean.py` loads `cleanProductInfo.json` and normalizes to pandas DataFrame
2. Explode history array: `df.explode('history')` creates one row per product-price entry
3. Flatten history objects: `pd.json_normalize()` extracts `daySinceEpoch` and `price` columns
4. Expected output: DataFrame schema = `[name, url, img, quantity, daySinceEpoch, price]`

### When Adding Features
- Maintain JSON schema consistency - e.g., all products must have `name`, `url`, `quantity`, `history`
- Price history array should never be empty (minimum one historical entry required)
- Preserve source URLs unchanged (used for chain identification and verification)

## Common Tasks

### Filtering/Comparing Products
- Filter by supermarket chain: Parse `url` field (Coles = `coles.com.au`, Aldi = `aldi.com.au`)
- Time-based analysis: Convert `daySinceEpoch` to dates as needed (days since Unix epoch)
- Product matching: `name` field may have duplicates across chains; URL is unique identifier

### Extending Data Processing
- Current: DataFrame head() output only; expand with aggregations, price trend analysis, or cross-chain comparisons
- JSON file is large (~156K lines); consider chunking for memory-intensive operations
