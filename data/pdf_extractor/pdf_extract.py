import pandas as pd
from pypdf import PdfReader
import  pdfplumber
import re
# py -m pip install requests
from tabula import read_pdf
from tabulate import tabulate
import camelot

# extract all the tables in the PDF file
abc = read_pdf(r"C:\Users\jpark\VSCode\gdp_income\data\pdf_extractor\imf_iso3.pdf", pages="all")   #address of file location
 
page1 = abc[0].iloc[4:, [0,1]]
page2 = abc[2].iloc[4:, [0,1]]
page3 = abc[4].iloc[4:, [0,1]]

imf_iso3codes = pd.concat([page1, page2, page3])
#imf_iso3codes.to_csv("imf_iso3codes.csv")
# Data needs to be adjusted
imf_iso3codes = pd.read_csv("data\pdf_extractor\imf_iso3codes_revised.csv")
imf_iso3codes = imf_iso3codes.iloc[:, 1].to_frame()
imf_iso3codes = pd.DataFrame(imf_iso3codes['Unnamed: 0'].str.split(' ').tolist(), columns = ['imf_code','iso3_code'])

toAdd = pd.DataFrame(data=[354,352,351,867,323,887,823,319,326,859,816,954,928,839,829,312,187])
toAdd.columns = ['imf_code'] 
toAdd['iso3_code']= ['CUW','MAF','MSR','MHL','FLK','PYF','GIB','BMU','GRL','ASM','FRO','PRK','CUB','NCL','GUM','AIA','VAT']
imf_iso3codes = pd.concat([imf_iso3codes, toAdd])
imf_iso3codes.to_csv("data\pdf_extractor\imf_iso3codes_usethese.csv")