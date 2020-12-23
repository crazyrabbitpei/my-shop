import json
from datetime import date, timedelta
from .handlers import show_sales_detail


def my_scheduled_job(to_dir):
    data = show_sales_detail()
    print(data)
    d = date.today() - timedelta(days=1)
    with open(f'{to_dir}/{d.isoformat()}.json', 'w') as fp:
        json.dump(fp, data)
