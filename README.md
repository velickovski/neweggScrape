# Newegg Scraper

This repository contains a web scraping application that extracts data for 500 products from the Newegg website.

## Files

- `main.py`: This file contains the solution for scraping products from Newegg. It handles the basic web scraping functionality.
- `threads.py`: This is the optimal solution that utilizes threading to efficiently handle multiple requests simultaneously, improving the scraping speed and efficiency.

## Requirements

To run the application, ensure you have Python installed on your system. You may also need to install the required packages. You can do this using pip:

```bash
pip install -r requirements.txt
git clone https://github.com/velickovski/neweggScrape.git
cd neweggScrape
#1 Basic main
python main.py
#2 Advanced optimal solution
python threads.py
