import requests
import time
import os
import re
from bs4 import BeautifulSoup

def download_10k(ticker, email='your-email@example.com', base_dir='sec_downloads', years=None):
    """Download the complete 10-K filing for a given ticker"""
    
    # Create downloads directory
    os.makedirs(base_dir, exist_ok=True)
    
    headers = {
        'User-Agent': f'Company Research Tool ({email})',
        'Accept-Encoding': 'gzip, deflate'
    }

    try:
        print(f"\nProcessing {ticker}...")
        print("1. Getting company information...")
        
        # Step 1: Get the CIK number
        response = requests.get(
            'https://www.sec.gov/files/company_tickers.json',
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get company tickers: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        companies_data = response.json()
        cik = None
        
        for entry in companies_data.values():
            if entry['ticker'].upper() == ticker.upper():
                cik = str(entry['cik_str']).zfill(10)
                break
        
        if not cik:
            print(f"❌ Could not find CIK for {ticker}")
            return False
            
        print(f"✅ Found CIK: {cik}")
        time.sleep(2)  # SEC rate limit

        # Step 2: Get company's submissions
        company_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        headers['Host'] = 'data.sec.gov'
        response = requests.get(company_url, headers=headers)
        time.sleep(2)  # SEC rate limit
        
        if response.status_code != 200:
            print(f"❌ Error accessing SEC data: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        filings = response.json()
        print("2. Looking for most recent 10-K...")
        
        recent_filings = filings['filings']['recent']
        found = False
        downloaded_count = 0
        
        # Look for both '10-K' and '20-F' (foreign company annual report)
        for i, form in enumerate(recent_filings['form']):
            if form in ['10-K', '20-F']:
                filing_date = recent_filings['filingDate'][i]
                filing_year = int(filing_date.split('-')[0])
                
                # Skip if not in requested years
                if years and filing_year not in years:
                    continue

                found = True
                accession_number = recent_filings['accessionNumber'][i]
                
                print(f"✅ Found {form} filed on {filing_date}")

                # Construct EDGAR URL
                acc_no_stripped = accession_number.replace('-', '')
                url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_stripped}/{accession_number}.txt"

                headers['Host'] = 'www.sec.gov'
                response = requests.get(url, headers=headers)
                time.sleep(2)  # SEC rate limit

                if response.status_code == 200:
                    company_dir = os.path.join(base_dir, ticker)
                    os.makedirs(company_dir, exist_ok=True)

                    raw_filename = os.path.join(company_dir, f'{form}_{filing_date}_full.txt')
                    html_filename = os.path.join(company_dir, f'{form}_{filing_date}.html')

                    with open(raw_filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    # Save HTML version
                    soup = BeautifulSoup(response.text, 'html.parser')
                    with open(html_filename, 'w', encoding='utf-8') as f:
                        f.write(str(soup))

                    print(f"✅ Saved: {raw_filename} & {html_filename}")
                    downloaded_count += 1
                else:
                    print(f"❌ Failed to download document: {response.status_code}")
                    continue

        if not found:
            print("❌ No 10-K or 20-F filings found")
            return False
            
        return downloaded_count > 0
            
    except Exception as e:
        print(f"❌ Error processing {ticker}: {str(e)}")
        return False
