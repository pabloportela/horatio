import argparse
import csv
from collections import defaultdict
import sys

from horatio.ranking import Ranking


def warn(msg):
    ''' logs to stderr '''
    print(msg, file=sys.stderr)


def parse_csv_as_dict_list(filename):
    try:
        with open(filename) as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        raise Exception('Unable to parse csv file {}: {}'.format(filename, str(e)))


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

    try:
        with open(output_filename, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(output)
    except Exception as e:
        raise Exception('Unable to write output file {}: {}'.format(output_filename, str(e)))


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


def remove_barcode_dupes(barcodes):
    unique_barcodes = set()
    barcode_dupes = set()

    for row in barcodes:
        if row['barcode'] in unique_barcodes:
            barcode_dupes.add(row['barcode'])
        else:
            unique_barcodes.add(row['barcode'])

    if barcode_dupes:
        warn('\nIgnoring orders for duplicate barcodes: {}.\n'.format(', '.join(barcode_dupes)))

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
        sorted_ids = sorted(order_ids_without_barcode)
        warn('Ignoring orders without barcode: {}.\n'.format(', '.join(sorted_ids)))

    return orders_with_barcodes


def run(orders_filename, barcodes_filename, output_filename):
    ''' generate output file and print report '''

    # read input
    barcodes = parse_csv_as_dict_list(barcodes_filename)
    orders = parse_csv_as_dict_list(orders_filename)

    # validate, sanitize
    barcodes = remove_barcode_dupes(barcodes)
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


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process customers, orders and barcodes')
    parser.add_argument('--orders', type=str, help='orders csv file', default='orders.csv')
    parser.add_argument('--barcodes', type=str, help='barcodes csv file', default='barcodes.csv')
    parser.add_argument('--output', type=str, help='output csv file', default='output.csv')
    return parser.parse_args()


if __name__ == '__main__':

    try:
        arguments = parse_arguments()
        run(
            orders_filename=arguments.orders,
            barcodes_filename=arguments.barcodes,
            output_filename=arguments.output
        )
    except Exception as e:
        print(str(e))
