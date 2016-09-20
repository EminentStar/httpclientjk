import header_parser
import constants


def construct_get_request_msg(host, path, params, headers):
    request_message = 'GET '
    request_message += '/' + path

    if params:
        request_message += '?' + params
    header_str = header_parser.dict_to_header(host, headers)
    request_message += ' HTTP/1.1' + constants.CRLF + header_str + constants.CRLF
    request_message = request_message.encode()
    return request_message


def construct_post_request_msg(host, resource_location, headers, body_dict, form_data):
    request_message = 'POST '
    request_message += resource_location
    header_str = header_parser.dict_to_header(host, headers)
    
    request_body = construct_post_request_body(body_dict)
    header_str += 'Content-Length: %s%s' % (len(request_body.encode()), constants.CRLF)
    if form_data:
        header_str += multipart.construct_multipart_file_header_and_body()

    request_message += ' HTTP/1.1' + constants.CRLF + header_str + constants.CRLF
    request_message += request_body + constants.CRLF 

    request_message = request_message.encode()
    return request_message


def concat_chunked_msg(headers, chunked_msg):
    contents_parts = chunked_msg.split(constants.CRLF_ENCODED)
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


def deconstruct_response(response_chunk):
    response_list = response_chunk.split(constants.CRLF_ENCODED*2)
    headers = response_list[0].split(constants.CRLF_ENCODED)
    status_line = headers.pop(0)
    header_dict = header_parser.header_list_to_header_dict(headers)
    contents = response_list[1]
    return status_line, header_dict, contents


def decode_response_msg(status_line, header_dict, contents):
    decoded_status_line = status_line.decode()
    decoded_header_dict = {}
    for k in header_dict:
        decoded_header_dict[k.decode()] = header_dict[k].decode()
    decoded_contents = contents.decode()

    return decoded_status_line, decoded_header_dict, decoded_contents


def print_response_msg(status_line, response_header_dict, contents):
    print(status_line)
    for key, value in response_header_dict.items():
        print(key, ': ', value)
    print(contents)


def print_response_msg_with_decoding(status_line, response_header_dict, contents):
    print(status_line.decode())
    for key, value in response_header_dict.items():
        print(key.decode(), ': ', value.decode())
    print(contents.decode())


def construct_redirection_msg(response_header_dict):
    """request message 재구성 및 s.send"""
    new_request_header_dict = {}
    "리다이렉션시 바꿔야할 것은 Location 헤더를 Host로"
    new_host, new_path, new_params = url_parser.deconstruct_url(response_header_dict[b'Location'].decode())
    new_request_message = message_parser.construct_get_request_msg(
        new_host,
        new_path,
        new_params,
        new_request_header_dict)
    return new_request_message


def construct_post_request_body(data_dict):
    data_list = [key + '=' + value for key, value in data_dict.items()]
    message_body = '&'.join(data_list)
    return message_body

