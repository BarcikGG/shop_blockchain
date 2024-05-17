import datetime
import json


indexes = {
    344000: "Rostov",
    347900: "Taganrog",
    347901: "Taganrog 1",
    347902: "Taganrog 2",
    347903: "Taganrog 3",
    346780: "Azov",
    346781: "Azov 1",
    346782: "Azov 2",
    346783: "Azov 3",
}

def create_map(index_from, index_to):
    from_num_last = str(index_from)[5]
    from_num = str(index_from)[2]
    to_num = str(index_to)[2]
    to_num_last = str(index_to)[5]

    map = [str(index_from)]

    if(from_num == '4'):
        if(to_num == '4'):
            map.append(str(index_to))
        elif(to_num_last == '0'):
            map.append(str(index_to))
        else:
            map.append(str(index_to)[:-1]+ '0')
            map.append(str(index_to))
    else:
        if(from_num_last != '0'):
            map.append(str(index_from)[:-1]+ '0')
        map.append('344000')
        if(to_num != '4'):
            if(to_num_last != '0'):
                map.append(str(index_to)[:-1]+ '0')
            map.append(str(index_to))

    return map


mail_classes = {
    1: {'days': 5, 'price': 0.5},
    2: {'days': 10, 'price': 0.3},
    3: {'days': 15, 'price': 0.1}
}

def price(mail_class, weight, cost):
    need_days = mail_classes[mail_class]['days']
    price = mail_classes[mail_class]['price'] * float(weight)

    total_price = price + (cost* 0.1)

    print(f'days: {need_days}')
    print(f'total: {total_price}')


def getDate(start_time, end_time):
    dt = datetime.datetime(2024, 5, 16)
    days = (end_time//1000 - start_time//1000) // 5
    dt += datetime.timedelta(days=days)
    return dt.strftime("%d%m%Y")
            # 1715839200  1715887800
# print(getDate(1715839200800, 1715887800926))

# price(1, "10", 100)
map = create_map(346781, 346780)
# print(map)
# print(map[len(map) -1])
history = {}

new_transit = [{"worker": '123', "track": 'rr123NUM', "weight": '5'}]
history['rr123NUM'] = json.dumps(new_transit)

items = json.loads(history['rr123NUM'])
items.append({"worker": '456', "track": 'rr123NUM', "weight": '5.2'})
history['rr123NUM'] = json.dumps(items)

items = json.loads(history['rr123NUM'])
print(int(items[len(items) - 1]['worker'][2:]))

print(history)
# print(map.index('346780'))