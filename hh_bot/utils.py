import re

def extract_name_and_quantity(line):
    matches = re.findall(r"([А-я]+\n)|([А-я]+.?[а-я]*.[а-я]+)|(\d+.+\d)|(\d+)", line)
    exception = ['кг', 'шт', 'мл', 'ш т', 'л']
    quantity = '1'
    for match in matches:
        for group in match:
            if group != '' and group not in exception:
                if any(char.isdigit() for char in group):
                    quantity = group
                else:
                    name = group
    if ',' in quantity:
        quantity = quantity.replace(',', '.')
    return name, float(quantity)

def created_product_json(products_list, list_id, user_id):
    json_data = []
    status_price = '' 
    similar_name = '' 
    for line in products_list.split("\n"):
        name, quantity = extract_name_and_quantity(line)
        if name:
            json_data.append({
                "name": name,
                "quantity": quantity,
                "price": 0,
                "status_price": status_price,
                "list_id": list_id,
                "user_id": user_id,
                "similar_name": similar_name
            })
    return json_data

