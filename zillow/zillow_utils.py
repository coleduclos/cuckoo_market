import argparse
from google.cloud import bigquery

def run_query(args):
    down_payment = args.down_payment
    down_payment_max = args.down_payment_max
    interest_rate = args.interest_rate
    limit = args.limit
    mortgage_length = args.mortgage_length
    sizerank_max = args.sizerank_max
    payments_per_year = 12
    n = mortgage_length * payments_per_year
    i = interest_rate / payments_per_year
    discount_factor =  ((1 + i)**n - 1) / (i * (1 + i)**n)

    query = f"""
SELECT regionname, state, sizerank, zri, zhvi, down_payment, mortgage_payment,
(zri - mortgage_payment) as profit
FROM (
    SELECT county_zri.regionname AS regionname,
    county_zri.state as state,
    county_zri.sizerank as sizerank,
    county_zri._2018_06 AS zri,
    county_zhvi._2018_06 AS zhvi,
    (county_zhvi._2018_06 * {down_payment}) AS down_payment,
    (county_zhvi._2018_06 * (1 - {down_payment})) / {discount_factor} AS mortgage_payment
    FROM `cuckoo-market-dev.zillow.county_zri` AS county_zri
    JOIN `cuckoo-market-dev.zillow.county_zhvi` AS county_zhvi
    ON county_zri.regionid = county_zhvi.regionid
    WHERE county_zri.sizerank < {sizerank_max}
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
    parser.add_argument('--sizerank_max',
            default=400,
            help='The size rank of the geographical region used to filter results.')
    args = parser.parse_args()

    run_query(args)

if __name__ == '__main__':
    main()
