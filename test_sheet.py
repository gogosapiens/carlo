from carlo.sheet import HorizontalSheet

sheet = HorizontalSheet("1z_1S5_qb4YEIymuvQ5QCYoL16sJ6BeYrvQ5QnRL0GMc", page="horizontal")
items = sheet.items
item = items[2]
# print(item)
#sheet.set_item_values(item, {"Value": "name8", "Date Upd": "Cool4", "Value Upd": "Cool5"})
#print(sheet.items)

items = [
    {"Value": "Super Mario", "Date Upd": "118", "Value Upd": "Luigi"},
    {"Value": "Super Mario Galaxy", "Date Upd": "119", "Value Upd": "Kirby"},
    {"Value": "Super Mario Galaxy 2", "Date Upd": "120", "Value Upd": "Yoshi"},
]
sheet.insert_items(items)
