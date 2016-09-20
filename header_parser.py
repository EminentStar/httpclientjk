import constants


def dict_to_header(host, header_dict):
    header_str = ''
    header_str += 'Host: %s%s' % (host, constants.CRLF)
    for key, value in header_dict.items():
        header_str += key + ': ' + value + constants.CRLF 
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


def is_chunked_encoded(response_header_dict):
    if b'Transfer-Encoding' in response_header_dict:
        if response_header_dict[b'Transfer-Encoding'] == b'chunked':
            return True
    return False

