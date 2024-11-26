import requests
import json
import csv
import sys
from typing import List, Dict
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from .env
API_KEY = os.getenv('CRUX_API_KEY')
API_ENDPOINT = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"

PERFORMANCE_THRESHOLDS = {
    'largest_contentful_paint': {'good': 2500, 'needs_improvement': 4000},
    'first_contentful_paint': {'good': 1800, 'needs_improvement': 3000},
    'interaction_to_next_paint': {'good': 200, 'needs_improvement': 500},
    'experimental_time_to_first_byte': {'good': 800, 'needs_improvement': 1800},
    'cumulative_layout_shift': {'good': 0.1, 'needs_improvement': 0.25}
}

def read_urls(file_path: str) -> List[str]:
    file_ext = Path(file_path).suffix
    if file_ext == '.csv':
        return pd.read_csv(file_path)['url'].tolist()
    elif file_ext == '.txt':
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    raise ValueError("Unsupported file format. Please use .csv or .txt")

def query_crux_api(url: str) -> Dict:
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "url": url,
        "metrics": [
            "largest_contentful_paint",
            "first_contentful_paint", 
            "interaction_to_next_paint",
            "experimental_time_to_first_byte",
            "cumulative_layout_shift"
        ]
    }
    
    response = requests.post(
        f"{API_ENDPOINT}?key={API_KEY}",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    data = response.json()
    print(f"\nAPI Response for {url}:")
    
    if 'error' in data:
        error = data['error']
        print(f"Error Code: {error.get('code')}")
        print(f"Status: {error.get('status')}")
        print(f"Message: {error.get('message')}")
    else:
        metrics = data.get('record', {}).get('metrics', {})
        for metric, values in metrics.items():
            if 'percentiles' in values:
                print(f"{metric}: p75={values['percentiles']['p75']}")
    
    return data

def extract_performance_data(data: Dict) -> Dict:
    metrics = data.get('record', {}).get('metrics', {})
    url = data.get('urlNormalizationDetails', {}).get('originalUrl', '')
    
    performance_data = {
        'URL': url,
        'Metric': [],
        'P75 Value': [],
        'Rating': [],
        'Good %': [],
        'Needs Improvement %': [],
        'Poor %': []
    }
    
    for metric_name, metric_data in metrics.items():
        if 'percentiles' in metric_data and 'histogram' in metric_data:
            p75 = metric_data['percentiles']['p75']
            histogram = metric_data['histogram']
            
            performance_data['Metric'].append(metric_name)
            performance_data['P75 Value'].append(p75)
            performance_data['Good %'].append(histogram[0]['density'] * 100)
            performance_data['Needs Improvement %'].append(histogram[1]['density'] * 100)
            performance_data['Poor %'].append(histogram[2]['density'] * 100)
            
            if metric_name in PERFORMANCE_THRESHOLDS:
                thresholds = PERFORMANCE_THRESHOLDS[metric_name]
                if float(str(p75)) <= thresholds['good']:
                    rating = 'Good'
                elif float(str(p75)) <= thresholds['needs_improvement']:
                    rating = 'Needs Improvement'
                else:
                    rating = 'Poor'
                performance_data['Rating'].append(rating)
            else:
                performance_data['Rating'].append('N/A')
    
    return performance_data

def extract_raw_metrics(data: Dict) -> Dict:
    # Get the metrics data
    metrics = data.get('record', {}).get('metrics', {})
    
    # Initialize base data
    raw_data = {
        'url': data.get('urlNormalizationDetails', {}).get('originalUrl', ''),
        'normalized_url': data.get('urlNormalizationDetails', {}).get('normalizedUrl', '')
    }
    
    # Extract all available metrics
    for metric_name in ['largest_contentful_paint', 'first_contentful_paint', 
                       'interaction_to_next_paint', 'experimental_time_to_first_byte',
                       'cumulative_layout_shift']:
        metric_data = metrics.get(metric_name, {})
        
        # Get p75 value
        if 'percentiles' in metric_data:
            raw_data[f"{metric_name}_p75"] = metric_data['percentiles'].get('p75', '')
        
        # Get histogram data
        if 'histogram' in metric_data:
            for idx, bucket in enumerate(metric_data['histogram'], 1):
                raw_data[f"{metric_name}_bucket_{idx}_density"] = bucket.get('density', '')
                raw_data[f"{metric_name}_bucket_{idx}_start"] = bucket.get('start', '')
                raw_data[f"{metric_name}_bucket_{idx}_end"] = bucket.get('end', '')
    
    # Add form factors if available
    if 'form_factors' in metrics:
        for device, fraction in metrics['form_factors'].get('fractions', {}).items():
            raw_data[f"form_factor_{device}"] = fraction
    
    return raw_data

def main(input_file: str, performance_output: str, raw_output: str):
    urls = read_urls(input_file)
    performance_results = []
    raw_results = []
    
    print(f"\nAnalyzing Core Web Vitals for {len(urls)} URLs...\n")
    print("=" * 50)
    
    for url in urls:
        try:
            data = query_crux_api(url)
            perf_data = extract_performance_data(data)
            raw_data = extract_raw_metrics(data)
            
            performance_results.append(perf_data)
            raw_results.append(raw_data)
            
            # Cleaner console output
            print(f"\n📊 {url}")
            print("─" * 50)
            
            metrics_display = {
                'largest_contentful_paint': 'LCP',
                'first_contentful_paint': 'FCP',
                'interaction_to_next_paint': 'INP',
                'experimental_time_to_first_byte': 'TTFB'
            }
            
            for i in range(len(perf_data['Metric'])):
                metric = perf_data['Metric'][i]
                if metric in metrics_display:
                    print(f"{metrics_display[metric]}: {perf_data['P75 Value'][i]}ms")
                    print(f"Rating: {perf_data['Rating'][i]}")
                    print(f"Good: {perf_data['Good %'][i]:.1f}% | Needs Improvement: {perf_data['Needs Improvement %'][i]:.1f}% | Poor: {perf_data['Poor %'][i]:.1f}%")
                    print("─" * 30)
            
        except Exception as e:
            print(f"❌ Error analyzing {url}: {str(e)}")
            continue
    
    # Save files
    perf_df = pd.DataFrame([{
        'URL': data['URL'],
        'Metric': metric,
        'P75 Value': value,
        'Rating': rating,
        'Good %': good,
        'Needs Improvement %': needs_improvement,
        'Poor %': poor
    } for data in performance_results
      for metric, value, rating, good, needs_improvement, poor in zip(
          data['Metric'], data['P75 Value'], data['Rating'],
          data['Good %'], data['Needs Improvement %'], data['Poor %']
      )])
    perf_df.to_csv(performance_output, index=False)
    
    raw_df = pd.DataFrame(raw_results)
    raw_df.to_csv(raw_output, index=False)
    
    print("\n" + "=" * 50)
    print(f"✅ Analysis complete!")
    print(f"📝 Performance summary: {performance_output}")
    print(f"📊 Raw metrics: {raw_output}\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python crux_api_analyzer.py <input_file> <performance_output.csv> <raw_metrics.csv>")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2], sys.argv[3])
