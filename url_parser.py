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


def get_port_from_host(host):
    port = 80
    host_parts = host.split(':', 1)
    if len(host_parts) != 1:
        port = int(host_parts[1])
    return port


def detach_scheme(url):
    scheme_index = url.index('//')
    detached_url = url[scheme_index + 2:]
    return detached_url

