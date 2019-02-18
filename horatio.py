import csv
from collections import defaultdict
import sys


def log(msg):
    ''' logs to stderr '''
    print(msg, file=sys.stderr)


def parse_csv_as_dict_list(filename):
    with open(filename) as f:
        reader = csv.DictReader(f)
        return list(reader)


def parse_customer_orders(orders):
    ''' returns a dict with list of order id's per customer id '''

    customer_orders = defaultdict(list)
    for row in orders:
        customer_orders[row['customer_id']].append(row['order_id'])

    return customer_orders


def parse_order_barcodes(barcodes):
    ''' returns a dict with list of barcodes per order id '''

    order_barcodes = defaultdict(list)
    for row in barcodes:
        order_barcodes[row['order_id']].append(row['barcode'])

    return order_barcodes


def get_output(customer_orders, order_barcodes):
    ''' generates output barcodes per order, per customer '''
    output = list()
    for customer_id, orders in customer_orders.items():
        for order_id in orders:
            output.append([customer_id, order_id] + order_barcodes[order_id])

    return output

def print_output(output, output_filename):
    ''' generates a csv file with output '''
    with open(output_filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(output)


def get_unused_barcode_amount(barcodes):
    return sum(1 for row in barcodes if row['order_id'] is '')


def print_unused_barcode_amount(barcodes):
    print('Amount of unused barcodes: {}\n'.format(get_unused_barcode_amount(barcodes)))


def get_customer_ticket_amount(customer_id, customer_orders, order_barcodes):
    return sum(len(order_barcodes[o_id]) for o_id in customer_orders[customer_id])


def get_customer_ranking(customer_orders, order_barcodes, length):
    ranking = Ranking(length)

    # relate customers to barcode quantity, add them to the ranking
    for c_id in customer_orders.keys():
        ranking.add(c_id, get_customer_ticket_amount(c_id, customer_orders, order_barcodes))

    # return length-sliced dict list
    return [{'customer_id': a[0], 'amount_of_tickets': a[1]} for a in ranking.get()]


def print_customer_ranking(ranking):
    print('Top {} Customers:'.format(len(ranking)))
    print('customer_id,amount_of_tickets')
    for row in ranking:
        print(row['customer_id'] + ',' + str(row['amount_of_tickets']))
    print()


class Ranking:
    ''' Builds a top-<length> ranking of <item> according to <value> '''

    def __init__(self, length):
        self.length = length
        self.items = list()
        self.min_value = -1

    def add(self, item, value):
        ''' adds to the ranking if item belongs, discards otherwise '''

        # discard unless ranking not complete or value below threshold
        if not (len(self.items) < self.length or value > self.min_value):
            return

        # append and sort
        self.items.append(tuple([item, value]))
        self.items.sort(key=lambda x: x[1], reverse=True)

        # cut out eventual item out of the ranking
        self.items = self.items[:self.length]

        # update entry barrier
        self.min_value = self.items[-1][1]

    def get(self):
        return self.items


def remove_barcode_dupes(barcodes):
    unique_barcodes = set()
    barcode_dupes = set()

    for row in barcodes:
        if row['barcode'] in unique_barcodes:
            barcode_dupes.add(row['barcode'])
        else:
            unique_barcodes.add(row['barcode'])

    if barcode_dupes:
        log('\nFound duplicate barcodes: {}.\nIgnoring such barcodes and related orders.\n'.format(', '.join(barcode_dupes)))

    return [row for row in barcodes if row['barcode'] not in barcode_dupes]


def remove_orders_without_barcodes(orders, order_ids_with_barcode):
    order_ids_without_barcode = set()
    orders_with_barcodes = list()
    for row in orders:
        if row['order_id'] not in order_ids_with_barcode:
            order_ids_without_barcode.add(row['order_id'])
        else:
            orders_with_barcodes.append(row)

    if order_ids_without_barcode:
        log('Found orders without barcode: {}.\nIgnoring them.\n'.format(', '.join(order_ids_without_barcode)))

    return orders_with_barcodes


def main():
    ''' generate output file and print report '''

    # define input and output files
    orders_filename = 'orders.csv'
    barcodes_filename = 'barcodes.csv'
    output_filename = 'output.csv'

    # read input
    barcodes = parse_csv_as_dict_list(barcodes_filename)
    barcodes = remove_barcode_dupes(barcodes)

    # validate, sanitize
    orders = parse_csv_as_dict_list(orders_filename)
    orders = remove_orders_without_barcodes(orders, set(row['order_id'] for row in barcodes))

    # generate data structures
    order_barcodes = parse_order_barcodes(barcodes)
    customer_orders = parse_customer_orders(orders)

    # outuput file
    output = get_output(customer_orders, order_barcodes)
    print_output(output, output_filename)

    # top 5 customers
    customer_ranking = get_customer_ranking(customer_orders, order_barcodes, 5)
    print_customer_ranking(customer_ranking)

    # unused barcode amount
    print_unused_barcode_amount(barcodes)


if __name__ == '__main__':
    main()
