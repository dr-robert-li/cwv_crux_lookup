# CrUX API Performance Analyzer

A Python tool that analyzes Core Web Vitals performance metrics using the Chrome User Experience Report (CrUX) API.

## Features

- Batch process multiple URLs from CSV or TXT files
- Analyze key Core Web Vitals metrics:
  - Largest Contentful Paint (LCP)
  - First Contentful Paint (FCP)
  - Interaction to Next Paint (INP)
  - Time to First Byte (TTFB)
- Generate performance ratings and distribution analysis
- Output detailed CSV reports with human-readable metrics

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage
Create a python virtual environment and activate it.


Run the script with:
```python
python crux_api_analyzer.py <input_file> <output_file.csv> <raw_metrics.csv>
```

## Input File Format
* CSV file with a 'url' column
* TXT file with one URL per line

## Output Format
The script generates one CSV file containing:

* URL and normalized URL
* P75 values for each metric (in milliseconds)
* Performance ratings (Good/Needs Improvement/Poor)
* Distribution percentages for each performance category

And another CSV file with raw metrics for each URL.

## Performance Thresholds

Metric	Good	Needs Improvement	Poor
LCP	≤2.5s	2.5s - 4.0s	>4.0s
FCP	≤1.8s	1.8s - 3.0s	>3.0s
INP	≤200ms	200ms - 500ms	>500ms
TTFB	≤800ms	800ms - 1800ms	>1800ms

## Example Outputs
```csv
URL,Metric,P75 Value,Rating,Good %,Needs Improvement %,Poor %
https://wpengine.com,largest_contentful_paint,2026,Good,84.1,11.8,4.1
https://wpengine.com,first_contentful_paint,1857,Needs Improvement,73.5,21.0,5.5
https://wpengine.com,interaction_to_next_paint,88,Good,93.9,4.7,1.4
https://wpengine.com,experimental_time_to_first_byte,893,Needs Improvement,70.5,26.3,3.2
```

```csv
url,normalized_url,largest_contentful_paint_p75,largest_contentful_paint_bucket_1_density,largest_contentful_paint_bucket_1_start,largest_contentful_paint_bucket_1_end,largest_contentful_paint_bucket_2_density,largest_contentful_paint_bucket_2_start,largest_contentful_paint_bucket_2_end,largest_contentful_paint_bucket_3_density,largest_contentful_paint_bucket_3_start,first_contentful_paint_p75,first_contentful_paint_bucket_1_density,first_contentful_paint_bucket_1_start,first_contentful_paint_bucket_1_end,first_contentful_paint_bucket_2_density,first_contentful_paint_bucket_2_start,first_contentful_paint_bucket_2_end,first_contentful_paint_bucket_3_density,first_contentful_paint_bucket_3_start,interaction_to_next_paint_p75,interaction_to_next_paint_bucket_1_density,interaction_to_next_paint_bucket_1_start,interaction_to_next_paint_bucket_1_end,interaction_to_next_paint_bucket_2_density,interaction_to_next_paint_bucket_2_start,interaction_to_next_paint_bucket_2_end,interaction_to_next_paint_bucket_3_density,interaction_to_next_paint_bucket_3_start,experimental_time_to_first_byte_p75,experimental_time_to_first_byte_bucket_1_density,experimental_time_to_first_byte_bucket_1_start,experimental_time_to_first_byte_bucket_1_end,experimental_time_to_first_byte_bucket_2_density,experimental_time_to_first_byte_bucket_2_start,experimental_time_to_first_byte_bucket_2_end,experimental_time_to_first_byte_bucket_3_density,experimental_time_to_first_byte_bucket_3_start
https://wpengine.com,https://wpengine.com/,2026,0.8411,0,2500,0.1176,2500,4000,0.0413,4000,1857,0.7351,0,1800,0.2101,1800,3000,0.0547,3000,88,0.9388,0,200,0.0471,200,500,0.0141,500,893,0.705,0,800,0.2631,800,1800,0.0319,1800
```

## Requirements
Python 3.7+
See requirements.txt for package dependencies


## License

MIT License

Copyright (c) 2024 Robert Li

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.