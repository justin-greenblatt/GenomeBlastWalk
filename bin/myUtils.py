from requests import get

def downloadFromURL(url, filename = False):
    if not filename:
        filename = url.split('/')[-1]
    h = open(filename, 'wb+')
    r = get(url, stream=True, allow_redirects=True)
    h.write(r.content)
    return filename