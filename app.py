from flask import Flask, render_template, request, jsonify, send_file
from sec_downloader import download_10k
import re
import os
import zipfile
from io import BytesIO
import tempfile
import logging
from flask_cors import CORS
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Vercel deployment

# Error handlers for Vercel
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(504)
def gateway_timeout_error(error):
    return jsonify({'error': 'Request timed out. Please try downloading fewer reports at once.'}), 504

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        logger.info(f"Received request data: {data}")
        
        email = data.get('email')
        tickers = data.get('tickers', [])
        years = data.get('years', [])
        
        # Input validation
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'error': 'Please provide a valid email address'}), 400
        
        if not tickers:
            return jsonify({'error': 'Please provide at least one ticker symbol'}), 400
            
        if len(tickers) > 5:  # Reduced max tickers for serverless
            return jsonify({'error': 'Maximum 5 ticker symbols allowed in one request'}), 400

        if not years:
            return jsonify({'error': 'Please select at least one year'}), 400

        # Convert years to integers
        try:
            years = [int(year) for year in years]
        except ValueError:
            return jsonify({'error': 'Invalid year format'}), 400

        # Create a temporary directory in /tmp for Vercel
        temp_dir = os.path.join('/tmp', 'sec_downloads')
        os.makedirs(temp_dir, exist_ok=True)

        try:
            downloaded_files = []
            for ticker in tickers:
                try:
                    logger.info(f"Downloading data for {ticker}")
                    success = download_10k(ticker, email, base_dir=temp_dir, years=years)
                    if not success:
                        return jsonify({'error': f'Failed to download data for {ticker}. Please verify the ticker symbol is correct.'}), 400
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {str(e)}")
                    return jsonify({'error': str(e)}), 400

            # Create zip file in memory
            memory_file = BytesIO()
            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        try:
                            zf.write(file_path, arcname)
                            downloaded_files.append(arcname)
                        except Exception as e:
                            logger.error(f"Error adding file to zip: {str(e)}")
                            return jsonify({'error': 'Error creating zip file'}), 500

            if not downloaded_files:
                return jsonify({'error': 'No files were downloaded'}), 400

            memory_file.seek(0)
            logger.info(f"Successfully created zip file with {len(downloaded_files)} files")

            response = send_file(
                memory_file,
                mimetype='application/zip',
                as_attachment=True,
                download_name='sec_filings.zip'
            )
            
            # Add CORS headers
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            return jsonify({'error': str(e)}), 500
        finally:
            # Cleanup temporary files
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"Error cleaning up temporary files: {str(e)}")

    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON in request'}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
