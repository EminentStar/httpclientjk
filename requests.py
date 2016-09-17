import socket

BUFFER_SIZE = 1024


def get(url, headers={}):
	host, path, params = deconstruct_url(url)
	port = get_port_from_host(host)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host + path, port))
	
	request_message = construct_get_request_msg(
			host, path, params, headers
			)
	s.send(request_message)
	response_message = b'' 
	
	first_recv = True
	while True:
		response = s.recv(BUFFER_SIZE)
		if first_recv is True:
			first_recv = False
			status_line, response_header_dict, contents = deconstruct_response(response)
			status_code = extract_status_code(status_line) 
		
			if is_redirection_response(status_code):
				new_request_message = construct_redirection_msg(response_header_dict)
				s.send(new_request_message)
				first_recv = True
			elif is_client_error_response(status_code): 
				""" chunk 인코딩 헤더가 있으면 contents 연결 """
				if is_chunked_encoded(response_header_dict) is True:
					contents = concat_chunked_msg(response_header_dict, contents)
				print_response_msg(status_line, response_header_dict, contents)			
		else: 
			contents += response
	
		if response == b'': 
			break
	
	s.close()
	if is_chunked_encoded(response_header_dict) is True:
		contents = concat_chunked_msg(response_header_dict, contents)
	return decode_response_msg(status_line, response_header_dict, contents)


def post(host, resource_location, data, headers={}):
	port = get_port_from_host(host)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	
	request_message = construct_post_request_msg(
			host, resource_location, headers, data
			)
	s.send(request_message)
	response_message = b'' 
	
	first_recv = True
	while True:
		response = s.recv(BUFFER_SIZE)
		if first_recv is True:
			first_recv = False
			status_line, response_header_dict, contents = deconstruct_response(response)
			status_code = extract_status_code(status_line) 
			
			if is_redirection_response(status_code):
				new_request_message = construct_redirection_msg(response_header_dict)
				s.send(new_request_message)
				first_recv = True
			elif is_client_error_response(status_code):
				""" chunk 인코딩 헤더가 있으면 contents 연결 """
				if is_chunked_encoded(response_header_dict) is True:
					contents = concat_chunked_msg(response_header_dict, contents)
				print_response_msg(status_line, response_header_dict, contents)			
		else: 
			contents += response
		if response == b'': 
			break
	
	s.close()
	
	if is_chunked_encoded(response_header_dict) is True:
		contents = concat_chunked_msg(response_header_dict, contents)
	
	return decode_response_msg(status_line, response_header_dict, contents)


def is_redirection_response(status_code):
	return status_code.startswith(b'3') is True


def is_client_error_response(status_code):
	return status_code.startswith(b'4') is True


def construct_redirection_msg(response_header_dict):
	"""request message 재구성 및 s.send"""
	new_request_header_dict = {}	
	"리다이렉션시 바꿔야할 것은 Location 헤더를 Host로"
	new_host, new_path, new_params = deconstruct_url(response_header_dict[b'Location'].decode())
	new_request_message = construct_get_request_msg(new_host, new_path, new_params,new_request_header_dict)
	return new_request_message


def is_chunked_encoded(response_header_dict):
	if b'Transfer-Encoding' in response_header_dict:
		if response_header_dict[b'Transfer-Encoding'] == b'chunked':
			return True
	return False


def print_response_msg(status_line, response_header_dict, contents):
	print(status_line)
	for key, value in response_header_dict.items():
		print(key, ': ', value)
	print(contents)


def decode_response_msg(status_line, header_dict, contents):
	decoded_status_line = status_line.decode()
	decoded_header_dict = {}
	for k in header_dict:
		decoded_header_dict[k.decode()] = header_dict[k].decode()
	decoded_contents = contents.decode()

	return decoded_status_line, decoded_header_dict, decoded_contents


def deconstruct_response(response_chunk):
	response_list = response_chunk.split(b'\r\n\r\n')
	
	headers = response_list[0].split(b'\r\n')
	status_line = headers.pop(0)
	header_dict = header_list_to_header_dict(headers)
	
	contents = response_list[1]
	return status_line, header_dict, contents


def detach_scheme(url):
	scheme_index = url.index('//')
	detached_url = url[scheme_index + 2:]
	return detached_url


def concat_chunked_msg(headers, chunked_msg):
	contents_parts = chunked_msg.split(b'\r\n')
	chunked_len = int(contents_parts[0], 16)
	concat_msg = b''
	is_trailer = False
	

	for item in contents_parts[1:]:
		if is_trailer is False:
			if chunked_len == 0:
				chunked_len = int(item, 16)
			else:
				concat_msg += item
				chunked_len -= len(item)
			if item == b'0':
				is_trailer = True
		elif is_trailer is True and item != b'': # trailer를 header목록에 넣는다.
			header_parts = item.split(b': ', 1)
			headers[header_parts[0]] = header_parts[1]
			
	return concat_msg


def construct_post_request_body(data_dict):
	data_list = [key + '=' + value for key, value in data_dict.items()]
	message_body = '&'.join(data_list)
	return message_body


def construct_post_request_msg(host, resource_location, headers, body_dict):
	request_message = 'POST '
	request_message += resource_location
	
	header_str = dict_to_header(host, headers)

	request_body = construct_post_request_body(body_dict)
	header_str += 'Content-Length: %s\r\n' % len(request_body.encode())

	request_message += ' HTTP/1.1\r\n' + header_str + '\r\n'
	request_message += request_body + '\r\n' 

	request_message = request_message.encode()
	
	return request_message


def construct_get_request_msg(host, path, params, headers):
	request_message = 'GET '
	request_message += '/' + path

	if params:
		request_message += '?' + params
	
	header_str = dict_to_header(host, headers)
	request_message += ' HTTP/1.1\r\n' + header_str + '\r\n'
	request_message = request_message.encode()
	
	return request_message


def get_port_from_host(host):
	port = 80
	host_parts = host.split(':', 1)
	if len(host_parts) != 1:
		port = int(host_parts[1])
	return port


def dict_to_header(host, header_dict):
	header_str = ''
	header_str += 'Host: %s\r\n' % host
	for key, value in header_dict.items():
		header_str += key + ': ' + value + '\r\n'
	return header_str


def header_list_to_header_dict(header_list):
	header_dict = {}
	for element in header_list:
		header_dict.update(header_to_dict(element))
	return header_dict


def header_to_dict(header_str):
	field_name, field_value = header_str.split(b': ')
	return {field_name: field_value}


def extract_status_code(status_line):
	status_line_list = status_line.split(b' ')
	return status_line_list[1]


def deconstruct_url(url):
	url_parts = url.split('/', 1)
	host = url_parts[0]
	path = ''
	params = ''
	if len(url_parts) != 1:
		path = url_parts[1]
		path_parts = path.split('?', 1)
		path = path_parts[0]
		
		if len(path_parts) != 1:
			params = path_parts[1]
	
	return host, path, params

