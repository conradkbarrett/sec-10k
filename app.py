from flask import Flask, render_template, request, jsonify, send_file
from sec_downloader import download_10k
import re
import os
import zipfile
from io import BytesIO
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        logger.info(f"Received request data: {data}")
        
        email = data.get('email')
        tickers = data.get('tickers', [])
        years = data.get('years', [])
        
        logger.info(f"Processing request for email: {email}, tickers: {tickers}, years: {years}")
        
        # Convert years to integers
        years = [int(year) for year in years]
        
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'error': 'Please provide a valid email address'}), 400
        
        if not tickers:
            return jsonify({'error': 'Please provide at least one ticker symbol'}), 400
            
        if len(tickers) > 20:
            return jsonify({'error': 'Maximum 20 ticker symbols allowed'}), 400

        if not years:
            return jsonify({'error': 'Please select at least one year'}), 400

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                downloads_dir = os.path.join(temp_dir, 'sec_downloads')
                os.makedirs(downloads_dir, exist_ok=True)

                for ticker in tickers:
                    try:
                        logger.info(f"Downloading data for {ticker}")
                        success = download_10k(ticker, email, base_dir=downloads_dir, years=years)
                        if not success:
                            return jsonify({'error': f'Failed to download data for {ticker}. Please verify the ticker symbol is correct.'}), 400
                    except Exception as e:
                        logger.error(f"Error processing {ticker}: {str(e)}")
                        return jsonify({'error': f'Error processing {ticker}: {str(e)}'}), 400

                memory_file = BytesIO()
                with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(downloads_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, downloads_dir)
                            zf.write(file_path, arcname)

                memory_file.seek(0)
                logger.info("Successfully created zip file")

                return send_file(
                    memory_file,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name='sec_filings.zip'
                )

            except Exception as e:
                logger.error(f"Server error: {str(e)}")
                return jsonify({'error': f'Server error: {str(e)}'}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
