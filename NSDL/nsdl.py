import concurrent.futures
import os
import dill
import PyPDF2
import pikepdf as pikepdf
import pandas as pd


class Read_NSDL(object):

    def __init__(self, person):
        self.person = person
        self.name = person.name.upper()
        self.nsdls_path = self.get_nsdl_path()
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #        executor.map(self.processor, self.nsdls_path)
        for p in self.nsdls_path:
            self.processor(p)

    def get_nsdl_path(self):
        files = os.listdir('NSDL/statements/')
        nsdls = []
        for f in files:
            if 'NSDLe-CAS' in f:
                nsdls.append('NSDL/statements/' + f)
        return nsdls

    def processor(self, np):
        month = np[-len('____2020.PDF'): -len('2020')]
        month = month.lower().capitalize()
        month = str(pd.to_datetime(month, format='%b_%Y'))
        self.decrypt_pdf(np, month, self.person.pan)
        self.read_pdf(month)

    def decrypt_pdf(self, input_path, output_path, password):
        try:
            with pikepdf.open(input_path, password=password) as pdf:
                del pdf.pages[0]
                del pdf.pages[-1]
                pdf.save(f"{output_path}.pdf")
        except pikepdf.PasswordError:
            print('Incorrect password')

    def read_pdf(self, _):
        pdfFileObj = open(f'{_}.pdf', 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        no_of_pages = pdfReader.numPages
        for i in range(no_of_pages):
            pageObj = pdfReader.getPage(i)
            text_on_page = pageObj.extractText()
            if "Holdings as on" in text_on_page and "Summary of value of holdings of" in text_on_page:
                holdings = self.get_holdings(text_on_page=text_on_page)
                self.add_holdings_to_record(_, holdings)
            if "No. of SharesMarket Price in `Value in `" in text_on_page:
                final = self.format_equity_string(text_on_page)
                for c in final:
                    company, c = self.get_company_name(c)
                    to_dissect, to_equal = self.get_volume_string(c)
                    no_of_shares, market_price = self.get_price_quantity(to_dissect, to_equal)
                    self.add_stock_to_record(company, _, no_of_shares, market_price)
            if 'Mutual Funds (M)ISINISIN DescriptionNo. of UnitsNAV in `Value in `' in text_on_page:
                final = self.format_mutual_funds_string(text_on_page)
                for mf in final:
                    mf_name, index = self.get_mf_name(mf)
                    quantity, nav = self.get_quantity_nav(mf, index)
                    self.add_mf_to_record(mf_name, _, quantity, nav)

        os.remove(f'{_}.pdf')

    def get_holdings(self, text_on_page):
        pos1 = text_on_page.find(self.name)
        pos2 = text_on_page.find("Holdings as on")
        holdings = text_on_page[pos1 + len(self.name) + 2: pos2]
        holdings = holdings.replace(',', '')
        holdings = float(holdings)
        self.person.holdings = holdings
        return holdings

    def get_mf_name(self, mf):
        for i in range(len(mf)):
            try:
                _ = int(mf[i])
                index = i
                break
            except:
                continue
        mf_name = mf[:index]
        return mf_name, index

    def format_mutual_funds_string(self, text_on_page):
        fstring = 'Mutual Funds (M)ISINISIN DescriptionNo. of UnitsNAV in `Value in `'
        pos1 = text_on_page.find(fstring)
        text = text_on_page[pos1 + len(fstring):]
        posend = text.find('Sub Total')
        text = text[:posend]
        rows = text.split('INF')[1:]
        prep = [p[len('204KB17I5'):] for p in rows]
        final = [f.replace('INF', '') for f in prep]
        return final

    def format_equity_string(self, text_on_page):
        fstring = "No. of SharesMarket Price in `Value in `"
        pos1 = text_on_page.find(fstring) + len(fstring)
        posend = text_on_page.find('Sub Total')
        text = text_on_page[pos1:posend + 1]
        rows = text.split('.NSE')[1:]
        final = []
        for row in rows:
            i = row.find("INE")
            final.append(row[:i])
        return final

    def get_company_name(self, c):
        pos3 = c.find("LIMITED") + len("LIMITED")
        company = c[0:pos3]
        c = c[pos3:]
        return company, c

    def get_volume_string(self, c):
        pos4 = c.find('.') + 3
        c = c[pos4:]
        pos5 = c.find('.') + 3
        to_dissect = c[:pos5]
        to_dissect = to_dissect.replace(',', '')
        to_equal = c[pos5:]
        to_equal = to_equal.replace(',', '')
        pos6 = to_equal.find('.') + 3
        to_equal = to_equal[:pos6]
        return to_dissect, to_equal

    def get_price_quantity(self, to_dissect, to_equal):
        for i in range(1, len(str(to_dissect))):
            no1 = float(to_dissect[:i])
            no2 = float(to_dissect[i:])
            actual = round(no1 * no2, 3)
            expected = round(float(to_equal), 3)
            if actual == expected:
                no_of_shares = int(no1)
                market_price = no2
                return no_of_shares, market_price

    def add_stock_to_record(self, company, month, no_of_shares, market_price):
        stock_df = pd.DataFrame({ 'Date': [month],
                                  'Company': [company],
                                  'Quantity': [no_of_shares],
                                  'Market_Price': [market_price]
                                  })
        self.add_to_record(stock_df, 'stocks')

    def add_holdings_to_record(self, month, holdings):
        holdings_df = pd.DataFrame({ 'Date': [month],
                                     'Holdings': holdings })
        self.add_to_record(holdings_df, 'holdings')

    def add_to_record(self, df, sheet):
        import sqlite3
        cnx = sqlite3.connect('financial.db')
        try:
            curr_df = pd.read_sql(f'select * from {str(sheet)}', cnx)
            final_df = curr_df.append(df)
            final_df = final_df.drop_duplicates()
        except:
            final_df = df
        final_df.to_sql(name=sheet, con=cnx, if_exists='replace', index=False)

    def get_quantity_nav(self, mf, index):
        text = mf[index:]
        pos1 = text.find('.')
        quantity = float(text[:pos1 + 4])
        text = text[pos1 + 4:]
        pos2 = text.find('.')
        nav = float(text[:pos2 + 5])
        return quantity, nav

    def add_mf_to_record(self, mf_name, month, quantity, nav):
        mf_df = pd.DataFrame({ 'Date': [month],
                               'Mutual_Fund_Name': [mf_name],
                               'Quantity': [quantity],
                               'NAV': [nav]
                               })
        self.add_to_record(mf_df, 'mutual_funds')