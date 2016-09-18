import requests

# GET method
status_line, headers, contents = requests.get('www.naver.com')

print(contents)
print(status_line)
print(headers)

# POST method
request_header = {'Content-type': 'text/plain'}
data = {'item': 'bandsaw 2647'}

status_line, headers, contents = requests.post('www.joes-hardware.com', '/inventory-check.cgi',
        data, request_header)

print(contents)
print(status_line)
print(headers)
