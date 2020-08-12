from NSDL.nsdl import Read_NSDL
from Classes.classes import Person
import time


if __name__ == '__main__':
    start_time = time.time()
    #Your name below and PAN Card Number
    p = Person('Full Name', 'PANCARDNO.')
    try:
        Read_NSDL(person=p)
    except Exception as e:
        print(e)
    print("Program took", time.time() - start_time, "to run")
