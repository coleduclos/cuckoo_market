import argparse
from google.cloud import bigquery

def run_query(query, destination_table=''):
    print(f"Running query: {query}")
    client = bigquery.Client()
    job_config = bigquery.QueryJobConfig()
    if destination_table:
        print(f'Writing results to {destination_table}...')
        table_ref = client.dataset('zillow').table(destination_table)
        job_config.destination = table_ref
        job_config.write_disposition = 'WRITE_TRUNCATE'
    query_job = client.query(query,
        job_config=job_config)
    results = query_job.result()
    for row in results:
        print(row)

def calculate_morgate_discount_factor(down_payment, interest_rate,
    mortgage_length, payments_per_year=12):
    n = mortgage_length * payments_per_year
    i = interest_rate / payments_per_year
    discount_factor =  ((1 + i)**n - 1) / (i * (1 + i)**n)
    return (1 - down_payment) / discount_factor

def zhvi_vs_mrp(args):
    discount_factor =  calculate_morgate_discount_factor(args.down_payment,
        args.interest_rate, args.mortgage_length)

    query = """
SELECT regionname, city, state, sizerank, median_rental_price, zhvi, down_payment, mortgage_payment,
(median_rental_price - mortgage_payment) as profit
FROM (
    SELECT {region_type}_median_rental_price_{property_type}.regionname AS regionname,
    {region_type}_median_rental_price_{property_type}.city as city,
    {region_type}_median_rental_price_{property_type}.state as state,
    {region_type}_median_rental_price_{property_type}.sizerank as sizerank,
    {region_type}_median_rental_price_{property_type}._2018_06 AS median_rental_price,
    {region_type}_zhvi_{property_type}._2018_06 AS zhvi,
    ({region_type}_zhvi_{property_type}._2018_06 * {down_payment}) AS down_payment,
    ({region_type}_zhvi_{property_type}._2018_06 * {discount_factor}) AS mortgage_payment
    FROM `cuckoo-market-dev.zillow.{region_type}_median_rental_price_{property_type}` AS {region_type}_median_rental_price_{property_type}
    JOIN `cuckoo-market-dev.zillow.{region_type}_zhvi_{property_type}` AS {region_type}_zhvi_{property_type}
    ON {region_type}_median_rental_price_{property_type}.regionname = {region_type}_zhvi_{property_type}.regionname
    AND {region_type}_median_rental_price_{property_type}.city = {region_type}_zhvi_{property_type}.city
    AND {region_type}_median_rental_price_{property_type}.state = {region_type}_zhvi_{property_type}.state
)
ORDER BY profit DESC
    """.format(discount_factor=discount_factor,
    down_payment=args.down_payment,
    property_type=args.property_type,
    region_type=args.region_type
    )

    destination_table=''
    if args.write:
        destination_table='{region_type}_zhvi_vs_mrp_profit_{property_type}'.format(region_type=args.region_type,
            property_type=args.property_type)
    run_query(query, destination_table=destination_table)

def zhvi_vs_zri(args):
    discount_factor =  calculate_morgate_discount_factor(args.down_payment,
        args.interest_rate, args.mortgage_length)

    query = """
SELECT regionname, city, state, sizerank, zri, zhvi, down_payment, mortgage_payment,
(zri - mortgage_payment) as profit
FROM (
    SELECT {region_type}_zri_{property_type}.regionname AS regionname,
    {region_type}_zri_{property_type}.city as city,
    {region_type}_zri_{property_type}.state as state,
    {region_type}_zri_{property_type}.sizerank as sizerank,
    {region_type}_zri_{property_type}._2018_06 AS zri,
    {region_type}_zhvi_{property_type}._2018_06 AS zhvi,
    ({region_type}_zhvi_{property_type}._2018_06 * {down_payment}) AS down_payment,
    ({region_type}_zhvi_{property_type}._2018_06 * {discount_factor}) AS mortgage_payment
    FROM `cuckoo-market-dev.zillow.{region_type}_zri_{property_type}` AS {region_type}_zri_{property_type}
    JOIN `cuckoo-market-dev.zillow.{region_type}_zhvi_{property_type}` AS {region_type}_zhvi_{property_type}
    ON {region_type}_zri_{property_type}.regionid = {region_type}_zhvi_{property_type}.regionid
)
ORDER BY profit DESC
    """.format(discount_factor=discount_factor,
    down_payment=args.down_payment,
    property_type=args.property_type,
    region_type=args.region_type
    )

    destination_table=''
    if args.write:
        destination_table='{region_type}_zhvi_vs_zri_profit_{property_type}'.format(region_type=args.region_type,
            property_type=args.property_type)
    run_query(query, destination_table=destination_table)

def main():
    parser = argparse.ArgumentParser(description='Zillow Utility')
    parser.add_argument('--down_payment',
            default=0.2,
            help='The down payment percentage used to calculate mortgage.')
    parser.add_argument('--interest_rate',
            default=0.05,
            help='The interest rate applied to the mortgage.')
    parser.add_argument('--mortgage_length',
            default=30,
            help='The total length of the mortgage in years.')
    parser.add_argument('--property_type',
            default='all',
            choices=['all','condo','sfr', '1br', '2br', '3br'],
            help='The total length of the mortgage in years.')
    parser.add_argument('--region_type',
            default='county',
            choices=['county','neighborhood'],
            help='The region type used to run the query.')
    parser.add_argument('--feature', action='store_true')
    parser.add_argument('--write',
            action='store_true',
            help='Write results to BigQuery table.')

    subparsers = parser.add_subparsers(help='sub-command help')
    zhvi_vs_zri_parser = subparsers.add_parser('zhvi_vs_zri', help='zhvi_vs_zri help')
    zhvi_vs_mrp_parser = subparsers.add_parser('zhvi_vs_mrp', help='zhvi_vs_mrp help')
    zhvi_vs_zri_parser.set_defaults(func=zhvi_vs_zri)
    zhvi_vs_mrp_parser.set_defaults(func=zhvi_vs_mrp)
    args = parser.parse_args()
    print(args)
    args.func(args)

if __name__ == '__main__':
    main()
