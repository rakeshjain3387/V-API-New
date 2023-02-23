data = []

result = []

for item in data:
    result.append({
        'username': item['mobile_number'],
        'password': item['password'],
        'config': {
            'max_sessions': 2
        }
    })

print(result)
