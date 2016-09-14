import socket


def get(url, headers):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((url, 80))
	header_str = dict_to_header(headers)
	request_message = 'GET ' + '/ HTTP/1.1\r\n' + header_str + '\r\n'
	request_message = request_message.encode()
	s.send(request_message)
	response_message = ""

	while True:
		response = s.recv(1024)
		if response == b'': break
		else: response_message += str(response)
	s.close()
	
	response_list = response_message.split('\\r\\n\\r\\n')
	
	headers = response_list[0].split('\\r\\n')
	status_line = headers.pop(0)
	status_code = status_line.split(' ')[1]
	contents = response_list[1]	
	header_dict = header_list_to_header_dict(headers)

	if status_code.startswith('3') is False:
		return header_dict, contents
	else:
		"""보류"""


def dict_to_header(header_dict):
	header_str = ''
	for key in header_dict.keys():
		header_str += key + ': ' + header_dict[key] + '\r\n'
	return header_str


def header_list_to_header_dict(header_list):
	header_dict = {}
	for element in header_list:
		header_dict.update(header_to_dict(element))
	return header_dict


def header_to_dict(header_str):
	field_name, field_value = header_str.split(': ')
	return {field_name: field_value}


def extract_status_code(status_line):
	status_line_list = status_line.split(' ')
	return status_line_list[1]


#headers = {}
#headers['Host'] = 'www.naver.com 80'

#get('www.naver.com', headers)

