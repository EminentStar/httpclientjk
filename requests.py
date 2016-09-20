import socket


import multipart
import header_parser
import url_parser
import message_parser
import constants


def get(url, headers={}):
    host, path, params = url_parser.deconstruct_url(url)
    port = url_parser.get_port_from_host(host)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host + path, port))

    s.settimeout(constants.TIMEOUT_SEC)

    request_message = message_parser.construct_get_request_msg(host, path, params, headers)
    s.send(request_message)
    response_message = b''
    

    first_recv = True
    while True:
        try:
            response = s.recv(constants.BUFFER_SIZE)
            if first_recv is True:
                first_recv = False
                status_line, response_header_dict, contents = message_parser.deconstruct_response(response)
                status_code = header_parser.extract_status_code(status_line)

                if is_redirection_response(status_code):
                    new_request_message = message_parser.construct_redirection_msg(response_header_dict)
                    s.send(new_request_message)
                    first_recv = True
                elif is_client_error_response(status_code):
                    # chunk 인코딩 헤더가 있으면 contents 연결
                    if header_parser.is_chunked_encoded(response_header_dict) is True:
                        contents = message_parser.concat_chunked_msg(response_header_dict, contents)
            else:
                contents += response

            if response == b'':
                break
        except socket.timeout:
            print('TCP timeout occured')
            break

    s.close()
    if header_parser.is_chunked_encoded(response_header_dict) is True:
        contents = message_parser.concat_chunked_msg(response_header_dict, contents)
    return message_parser.decode_response_msg(status_line, response_header_dict, contents)


def post(host, resource_location, data, form_data=[], headers={}):
    port = url_parser.get_port_from_host(host)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    request_message = message_parser.construct_post_request_msg(host, resource_location, headers, data, form_data)
    s.send(request_message)
    response_message = b''

    first_recv = True
    while True:
        response = s.recv(constants.BUFFER_SIZE)
        if first_recv is True:
            first_recv = False
            status_line, response_header_dict, contents = message_parser.deconstruct_response(response)
            status_code = header_parser.extract_status_code(status_line)

            if is_redirection_response(status_code):
                new_request_message = message_parser.construct_redirection_msg(response_header_dict)
                s.send(new_request_message)
                first_recv = True
            elif is_client_error_response(status_code):
                """ chunk 인코딩 헤더가 있으면 contents 연결 """
                if header_parser.is_chunked_encoded(response_header_dict) is True:
                    contents = message_parser.concat_chunked_msg(response_header_dict, contents)
                message_parser.print_response_msg_with_decoding(status_line, response_header_dict, contents)
        else:
            contents += response
        if response == b'':
            break

    s.close()

    if header_parser.is_chunked_encoded(response_header_dict) is True:
        contents = message_parser.concat_chunked_msg(response_header_dict, contents)
    return message_parser.decode_response_msg(status_line, response_header_dict, contents)


def is_redirection_response(status_code):
    return status_code.startswith(b'3') is True


def is_client_error_response(status_code):
    return status_code.startswith(b'4') is True


