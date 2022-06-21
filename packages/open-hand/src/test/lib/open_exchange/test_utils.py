
from lib.open_exchange.utils import clean_string_data

def test_clean_string_data():
    input = dict(
        req_okay='okay',
        req_bad=21,
        opt_okay='okay',
        opt_bad=42,
    )

    ## required
    ##   - not present
    ##   - present, wrong type
    ##   - present, correct type
    ## not required
    ##   - not present
    ##   - present, wrong type
    ##   - present, correct type

    clean_string_data(input, req_okay=True, req_bad=True, opt_okay=False, opt_bad=False)

    print(f"output = {input}")
