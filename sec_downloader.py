import requests
import time
import os
import re
from bs4 import BeautifulSoup

# List of companies to process
companies = [
    "PSO", "COUR", "CHGG", "TWOU", "STRA", "LRN", "ATGE", "LOPE", "PRDO",
    "MSFT", "GOOGL", "AMZN", "ADBE", "CRM", "ORCL", "IBM", "WDAY", "NOW",
    "TYL", "HPQ", "DELL", "VMW", "ADSK", "SPGI", "RHI", "VRSK", "MCO",
    "IQV", "PAYX", "AAPL", "META", "CSCO", "NVDA", "INTC", "ACN", "AVGO",
    "TXN", "MA", "V", "PYPL", "INTU", "AKAM", "FTNT", "PANW", "SPLK",
    "BLKB", "PWSC", "INST"
]

def extract_correct_10k(raw_text):
    """Finds the MAIN 10-K section and excludes exhibits and attachments."""
    documents = raw_text.split('<DOCUMENT>')

    ten_k_content = None
    mda_content = None

    print("🔍 Checking document types in SEC filing...")

    for doc in documents:
        doc_type_match = re.search(r'<TYPE>(.*?)\n', doc, re.IGNORECASE)
        doc_type = doc_type_match.group(1).strip() if doc_type_match else "UNKNOWN"
        print(f"🔹 Found document type: {doc_type}")

        # Ensure it's the main 10-K document, not an exhibit
        if doc_type == "10-K":
            print("✅ Identified the correct 10-K document!")
            ten_k_content = doc

            # Extract MD&A (Item 7)
            mda_match = re.search(r'(ITEM\s*7\.\s*MANAGEMENT\S*DISCUSSION\S*ANALYSIS.*?)ITEM\s*8', doc, re.DOTALL | re.IGNORECASE)
            if mda_match:
                mda_content = mda_match.group(1)

            break  # Stop once we find the correct 10-K document

    if not mda_content:
        mda_content = ten_k_content

    return ten_k_content, mda_content

def save_as_html(content, filename):
    """Converts extracted 10-K content to HTML and saves it."""
    soup = BeautifulSoup(content, "html.parser")

    # If the document is plain text, wrap it in <pre> tags
    if not soup.find():
        content = f"<html><body><pre>{content}</pre></body></html>"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

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
            # For BUD specifically, try alternative ticker
            if ticker.upper() == 'BUD':
                print("Trying alternative CIK lookup for BUD (Anheuser-Busch)")
                cik = '0001668717'.zfill(10)
            else:
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
            if form in ['10-K', '20-F']:  # Added 20-F for foreign companies
                filing_date = recent_filings['filingDate'][i]
                filing_year = int(filing_date.split('-')[0])
                
                # Skip if not in requested years
                if years and filing_year not in years:
                    continue

                found = True
                accession_number = recent_filings['accessionNumber'][i]
                
                print(f"✅ Found {form} filed on {filing_date}")

                # Construct EDGAR URL using different format
                acc_no_stripped = accession_number.replace('-', '')
                
                # Try both possible URL formats
                urls = [
                    f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_stripped}/{accession_number}.txt",
                    f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no_stripped}/{accession_number}.txt"
                ]

                success = False
                for url in urls:
                    print(f"Trying URL: {url}")
                    headers['Host'] = 'www.sec.gov'  # Reset host header for www.sec.gov
                    response = requests.get(url, headers=headers)
                    time.sleep(2)  # SEC rate limit

                    if response.status_code == 200:
                        success = True
                        break
                    else:
                        print(f"Failed with status {response.status_code}, trying alternative URL...")

                if success:
                    company_dir = os.path.join(base_dir, ticker)
                    os.makedirs(company_dir, exist_ok=True)

                    raw_filename = os.path.join(company_dir, f'{form}_{filing_date}_full.txt')
                    html_filename = os.path.join(company_dir, f'{form}_{filing_date}.html')

                    ten_k_content, _ = extract_correct_10k(response.text)

                    if ten_k_content:
                        with open(raw_filename, 'w', encoding='utf-8') as f:
                            f.write(ten_k_content)
                        save_as_html(ten_k_content, html_filename)
                        print(f"✅ Saved: {raw_filename} & {html_filename}")
                        downloaded_count += 1
                    else:
                        print("❌ No valid filing content found!")
                else:
                    print("❌ Failed to download document with all URL formats")
                    continue  # Try next filing if available

        if not found:
            print("❌ No 10-K or 20-F filings found")
            return False
            
        # Return True if we downloaded at least one filing
        return downloaded_count > 0
            
    except Exception as e:
        print(f"❌ Error processing {ticker}: {str(e)}")
        return False

# Comment out or remove the loop at the bottom since we'll be calling this from the web interface
# for company in companies:
#     download_10k(company)
#     time.sleep(2)
