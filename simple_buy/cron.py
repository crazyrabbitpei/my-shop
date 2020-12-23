import json
from .handlers import get_shop_handler


def my_scheduled_job(ofile):
    data = get_shop_handler('sales')
    print(data)
    #with open(ofile, 'w') as fp:
    #    json.dump(fp, )