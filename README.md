# Energy Bidding Optimizer

#### Project Status: [Discontinued]

## Project Intro
Built on Miriam Makhyoun's scripts, we hope to scrap CAISO day-ahead-market (DAM) and ancillary service (AS) bidding price to optimize energy bidding and correspondingly recommend DAM or ancillary bidding for clients. The ultimate goal is to produce a web app or GUI app to help clients to use this tool.
* build a data scrapping system to get hourly bidding price (DAM & AS)
* create a balance sheet to help clients to understand the most profitable bidding and hedging option

### Document Description
Original scripts:
* munging.py - pulls energy market prices via API into XML file  
* parse.py - parses XML data to convert it to a CSV file
* crunch.py - reads CSV file and allows users to input battery capacity (MW), charge/discharge efficiency (%), time to discharge battery (Hours), and the initial budget ($)

New scripts:
* main.py - combines the original three scripts and makes the scripts more accessible for clients
* ...

### Modules Used
* Data scrapping: `Requests`
* Data parsing: `ElementTree`
* ...

### Tools
* Python version 3.7.1

### Featured Deliverables
