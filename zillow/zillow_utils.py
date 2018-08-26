import argparse
from google.cloud import bigquery

def run_query(args):
    down_payment = args.down_payment
    down_payment_max = args.down_payment_max
    interest_rate = args.interest_rate
    limit = args.limit
    mortgage_length = args.mortgage_length
    region_type = args.region_type
    sizerank_max = args.sizerank_max
    payments_per_year = 12
    property_type = args.property_type
    n = mortgage_length * payments_per_year
    i = interest_rate / payments_per_year
    discount_factor =  ((1 + i)**n - 1) / (i * (1 + i)**n)

    query = f"""
SELECT regionname, state, sizerank, zri, zhvi, down_payment, mortgage_payment,
(zri - mortgage_payment) as profit
FROM (
    SELECT {region_type}_zri_{property_type}.regionname AS regionname,
    {region_type}_zri_{property_type}.state as state,
    {region_type}_zri_{property_type}.sizerank as sizerank,
    {region_type}_zri_{property_type}._2018_06 AS zri,
    {region_type}_zhvi_{property_type}._2018_06 AS zhvi,
    ({region_type}_zhvi_{property_type}._2018_06 * {down_payment}) AS down_payment,
    ({region_type}_zhvi_{property_type}._2018_06 * (1 - {down_payment})) / {discount_factor} AS mortgage_payment
    FROM `cuckoo-market-dev.zillow.{region_type}_zri_{property_type}` AS {region_type}_zri_{property_type}
    JOIN `cuckoo-market-dev.zillow.{region_type}_zhvi_{property_type}` AS {region_type}_zhvi_{property_type}
    ON {region_type}_zri_{property_type}.regionid = {region_type}_zhvi_{property_type}.regionid
    WHERE {region_type}_zri_{property_type}.sizerank < {sizerank_max}
)
WHERE down_payment < {down_payment_max}
ORDER BY profit DESC
LIMIT {limit}
    """
    print(f"Running query: {query}")
    client = bigquery.Client()
    query_job = client.query(query)
    results = query_job.result()
    for row in results:
        print(row)

def main():
    parser = argparse.ArgumentParser(description='Zillow Utility')
    parser.add_argument('--down_payment',
            default=0.2,
            help='The down payment percentage used to calculate mortgage.')
    parser.add_argument('--down_payment_max',
            default=60000,
            help='The maximum downpayment used to filter results.')
    parser.add_argument('--interest_rate',
            default=0.05,
            help='The interest rate applied to the mortgage.')
    parser.add_argument('--limit',
            default=100,
            help='Limit the number of results returned.')
    parser.add_argument('--mortgage_length',
            default=30,
            help='The total length of the mortgage in years.')
    parser.add_argument('--property_type',
            default='all',
            choices=['all','condo','sfr'],
            help='The total length of the mortgage in years.')
    parser.add_argument('--region_type',
            default='county',
            choices=['county','neighborhood'],
            help='The region type used to run the query.')
    parser.add_argument('--sizerank_max',
            default=400,
            help='The size rank of the geographical region used to filter results.')
    args = parser.parse_args()

    run_query(args)

if __name__ == '__main__':
    main()
