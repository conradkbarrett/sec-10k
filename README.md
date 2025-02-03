# 📊 SEC 10-K Downloader Web Service

A web interface for downloading SEC 10-K filings, built on top of [Natalia Zarina's SEC downloader script](https://github.com/NataliaZarina/sec-10k-downloader).

## Features

- 🌐 **Clean, iOS-style Web Interface**: Easy-to-use interface for downloading SEC filings
- 📅 **Multi-Year Selection**: Choose specific years to download filings from
- 🏢 **Multiple Companies**: Enter up to 20 ticker symbols at once
- 📦 **Automatic ZIP Packaging**: Downloads are automatically organized and zipped
- 🔄 **Real-time Status Updates**: See download progress and status in the interface
- 📄 **Support for Foreign Companies**: Downloads both 10-K and 20-F reports
- 💾 **Multiple Formats**: Saves reports in both .txt and .html formats

## How to Use

1. Visit the web interface
2. Enter your email (required by SEC for data access)
3. Enter ticker symbols (space-separated)
4. Select the years you want to download
5. Click "Download Reports"
6. Save the ZIP file containing all requested reports

## Technical Details

Built using:
- Flask (Python web framework)
- Modern HTML/CSS/JavaScript
- Original SEC downloading logic by Natalia (https://nataliaq.com)