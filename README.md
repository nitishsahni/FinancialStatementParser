# DematManager
- An NSDL-eCAS statement parser - automates the strenuous process of typing/writing it
- Can parse multiple statements for equity, mutual funds
- Stores all holdings data in an SQLite DB
- Use the parsed data to get a sense of financial allocations over time

# How it works
- Load all your NSDL-eCAS statements in the NSDL/statements folder
- Edit the main.py by passing in your legal name and PAN Card number as arguments in the Person class
- Run main.py (It parses 4 NSDL-eCAS statements in ~ 1 second)
- Used multithreading to achieve this speed

Currently only parses MFs and Equity
