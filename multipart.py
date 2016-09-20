import magic
import random

def construct_multipart_form_data_header(form_data):
    """
        dict in list형식의 form-data를 loop를 돌면서 header를 만든다.
    """
    multipart_header = ''

    # 첫번째 boundary를 생성한다.
    first_boundary = '%032x' % random.getrandbits(128)
    # Content-Type:  multipart/form-data의  header를 시작한다.
    multipart_header += 'Content-Type: multipart/form-data; '
    multipart_header += 'boundary=%s\r\n' % first_boundary
    """
        loop를 돌면서, 단순한 form element면 Content-Disposition과 form-data를 추가하고, 
        file이면 Content-Disposition, Content-Type, file data를 추가한다.
        file이 text형태가 아니라면 Content-Type-Encoding: binary를 생성한다.
            이때, file의 개수가 2개이상이라면 
            두번째 boundary를 생성하고 Content-Type: multipart/mixed의  해더를 시작한다.
            file을 전부 header에 넣었다면 두번째 boundary를 닫는다.
    """
    for element in form_data:
        (element_name, element_value), = element.items()
        multipart_header += '--' + first_boundary + '\r\n'
        if isinstance(element_value, list) is False: # file이 아닌 일반 form element를 의미한다.
            multipart_header += 'Content-Disposition: form-data; name ="%s"\r\n' % element_name
            multipart_header += '%s\r\n' % element_value
        else: # file의 집합일 때
            if len(element_value) == 1:
                multipart_header += 'Content-Disposition: form-data; ' 
                multipart_header += 'name= "%s"; filename="%s"\r\n' % (element_name, element_value)
                multipart_header += construct_multipart_file_header_and_body(element_value[0])
            else: # 2개 이상의 파일이 존재할 때
               second_boundary = '%032x' % random.getrandbits(128)
               multipart_header += 'Content-Disposition: form-data; name ="%s"\r\n' % element_name
               multipart_header += 'Content-Type: multipart/mixed; boundary=%s\r\n' % second_boundary 
               for filename in element_value:
                   multipart_header += '--' + second_boundary + '\r\n'
                   multipart_header += construct_multipart_file_header_and_body(filename)
               multipart_header += '--' + second_boundary + '--\r\n' 

    # multipart/form-data의 header를 마무리한다.
    multipart_header += '--' + first_boundary + '--\r\n'
    return multipart_header


def construct_multipart_file_header_and_body(filename):
    content_type = magic.from_file(filename, mime=True)
    result = 'Content-Type: ' + content_type + '\r\n'
    if 'text' not in content_type:
        result += 'Content-Transfer-Encoding: binary\r\n'

    file = open(filename, 'rb')
    bin_str = b''
    while True:
        fbyte = file.read(1)
        if fbyte == b'': break
        bin_str += fbyte
    file.close()
    result += str(bin_str) + '\r\n'
    return result

