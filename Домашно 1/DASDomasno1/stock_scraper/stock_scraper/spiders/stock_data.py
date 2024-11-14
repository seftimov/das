import scrapy
import csv
import os
import time
from datetime import datetime, timedelta


class StockDataSpider(scrapy.Spider):
    name = 'stock_data'
    allowed_domains = ['mse.mk']
    start_urls = ['https://www.mse.mk/en/stats/symbolhistory/ALK']
    csv_file_path = 'data/stock_data.csv'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.latest_dates = self.get_latest_dates()
        self.start_time = None

    def get_latest_dates(self):
        latest_dates = {}
        if os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    issuer_code = row['Issuer Code']
                    date_str = row['Date']
                    try:
                        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                    except ValueError:
                        self.logger.error(f"Invalid date format for issuer {issuer_code}: {date_str}")
                        continue
                    if issuer_code not in latest_dates or date_obj > latest_dates[issuer_code]:
                        latest_dates[issuer_code] = date_obj
        return latest_dates

    def start_requests(self):
        """Initiate the pipeline by requesting the page to retrieve all issuers."""
        self.start_time = time.time()
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.filter_retrieve_issuers)

    def filter_retrieve_issuers(self, response):
        """Filter 1: Automatically retrieve all issuers listed on the Macedonian Stock Exchange."""
        issuer_codes = response.xpath('//select[@id="Code"]/option[not(contains(@value, "\d"))]/@value').extract()
        self.logger.info(f"Retrieved Issuer Codes: {issuer_codes}")

        for code in issuer_codes:
            if not any(char.isdigit() for char in code):
                yield scrapy.Request(
                    url=f"https://www.mse.mk/en/stats/symbolhistory/{code}",
                    callback=self.filter_check_last_date,
                    meta={'issuer_code': code}
                )

    def filter_check_last_date(self, response):
        """Filter 2: Check the last date of available data and determine start date for fetching."""
        issuer_code = response.meta['issuer_code']
        last_date = self.latest_dates.get(issuer_code)
        start_date = last_date + timedelta(days=1) if last_date else datetime(datetime.now().year - 10, 1, 1)
        end_date = datetime.now()

        for year in range(start_date.year, end_date.year + 1):
            year_start = f"{year}-01-01"
            year_end = f"{year}-12-31" if year < end_date.year else end_date.strftime('%Y-%m-%d')
            yield scrapy.FormRequest(
                url=f"https://www.mse.mk/en/stats/symbolhistory/{issuer_code}",
                formdata={'FromDate': year_start, 'ToDate': year_end},
                callback=self.filter_fill_missing_data,
                meta={'issuer_code': issuer_code, 'year': year}
            )

    def filter_fill_missing_data(self, response):
        """Filter 3: Fill in missing data by adding only new records to the dataset."""
        issuer_code = response.meta['issuer_code']
        rows = response.xpath('//table[@id="resultsTable"]/tbody/tr')

        for row in rows:
            columns = row.xpath('td/text()').extract()
            if len(columns) >= 7:
                date_str = columns[0]
                date_obj = datetime.strptime(date_str, '%m/%d/%Y')

                if issuer_code in self.latest_dates and date_obj <= self.latest_dates[issuer_code]:
                    continue

                def format_price(value):
                    try:
                        value = float(value.replace(',', '').replace(' ', '').replace('€', '').strip())
                        return f"{value:,.2f}".replace(',', ' ').replace('.', ',').replace(' ', '.')
                    except ValueError:
                        return ''

                last_trade_price = format_price(columns[1])
                avg_price = format_price(columns[4])
                turnover_in_best = format_price(columns[7]) if len(columns) > 7 else ''
                total_turnover = format_price(columns[8]) if len(columns) > 8 else ''

                if len(columns) == 9:
                    yield {
                        'Issuer Code': issuer_code,
                        'Date': columns[0],
                        'Last Trade Price': last_trade_price,
                        'Max': format_price(columns[2]),
                        'Min': format_price(columns[3]),
                        'Avg. Price': avg_price,
                        '%chg.': columns[5],
                        'Volume': columns[6],
                        'Turnover in BEST': turnover_in_best,
                        'Total Turnover': total_turnover
                    }
                elif len(columns) == 7:
                    yield {
                        'Issuer Code': issuer_code,
                        'Date': columns[0],
                        'Last Trade Price': last_trade_price,
                        'Max': '',
                        'Min': '',
                        'Avg. Price': avg_price,
                        '%chg.': columns[3],
                        'Volume': columns[4],
                        'Turnover in BEST': turnover_in_best,
                        'Total Turnover': total_turnover
                    }

    def close(self, reason):
        """Log elapsed time when the spider finishes."""
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.logger.info(f"Spider finished. Elapsed time: {elapsed_time:.2f} seconds.")
