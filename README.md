# Horatio

Managing customers, orders and barcodes

## Getting Started


### Prerequisites

Python 3.6


### Installing

Just clone the repo :)

```
git clone git@github.com:pabloportela/horatio.git
```


### Running

This will run the script with barcodes.csv, orders.csv as input. Will use output.csv as output.

```
python3.6 -m horatio.horatio --orders data/orders.csv --barcodes data/barcodes.csv --output output.csv
```

### Testing

```
python3.6 -m unittest tests/test_integration.py
```
