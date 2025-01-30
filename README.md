# 📊 SEC 10-K Downloader

**A Python script that automatically downloads the latest 10-K financial filings and Management Discussion & Analysis (MD&A) reports from the SEC.**  

*Pulls the latest 10-K report for multiple companies (up to 40 at a time).*  
*Extracts the full financial report and management discussion.*
*Saves the report in `.txt` and `.html` formats for easy analysis.*
*Great for investors, analysts, and researchers.*

---

## **How to Install & Run This Tool**

### **1️⃣ Install Python (if you don’t have it already)**

If Python is not installed, download it here:
🔗 https://www.python.org/downloads/

2️⃣ Clone This Repository
To use this script, you need to download it to your computer.

git clone https://github.com/NataliaZarina/sec-10k-downloader.git
cd sec-10k-downloader

3️⃣ Install Required Python Packages
Before running the script, install the required libraries:

pip install -r requirements.txt

4️⃣ Update the Script with Your Email **(IMPORTANT)**
**SEC requires an email in the request headers.**

Open sec_downloader.py

Find this line:

headers = {
    'User-Agent': 'Company Research Tool (your-email@example.com)',
    'Accept-Encoding': 'gzip, deflate'
}

**Replace your-email@example.com with your own email.**
🚨 If you don’t update this, the SEC may block your requests.

5️⃣ Run the Script
Once everything is set up, run the script:

python sec_downloader.py

📂 Where Do the Files Go?

All downloaded reports are saved in a folder called sec_downloads/

Each company gets its own subfolder
Files are saved in both .txt and .html formats

⚠️ Troubleshooting & FAQs

Why is a company missing?
Some companies may not have filed a recent 10-K report.
Check manually on SEC EDGAR.

What if I get an error?
Make sure Python is installed and you have run pip install -r requirements.txt.
Check your internet connection.
**Ensure you replaced your email in sec_downloader.py.**

📜 License
This project is open-source under the MIT License.
Feel free to use & modify it!
