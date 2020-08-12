from Classes.classes import Person
import time
import dill
import os
import PyPDF2
import pikepdf as pikepdf
import pandas as pd


def run():
    start_time = time.time()
    with open('NSDL/models/nsdl.pkl', 'rb') as s:
        nsdl_reader = dill.load(s)
    try:
        p = Person('FULL NAME', 'PAN_NUMBER')
        # Example -> p = Person('Nitish Sahni', 'GBXPS0000T')
        nsdl_reader(p)
    except Exception as e:
        print(e)
    print("Program took", time.time() - start_time, "to run")


if __name__ == '__main__':
    run()
