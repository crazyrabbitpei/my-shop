import json
from datetime import date, timedelta
from .handlers import get_shop_handler


def my_scheduled_job(to_dir):
    data = get_shop_handler('sales', order='asc', order_by='total_amount', limit=-1)
    print(data)
    d = date.today() - timedelta(days=1)
    with open(f'{to_dir}/{d.isoformat()}', 'w') as fp:
        json.dump(fp, data)
