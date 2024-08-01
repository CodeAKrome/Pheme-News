from io import BytesIO
import pycurl

"""PyCurl wrapper with error lookup helpers."""
c = pycurl.Curl()


def cinfo(c):
    """All the PyCurl getinfo() values you could ever want/need"""
    return {
        "effective_url": c.getinfo(c.EFFECTIVE_URL),
        "response_code": c.getinfo(c.RESPONSE_CODE),
        "total_time": c.getinfo(c.TOTAL_TIME),
        "namelookup_time": c.getinfo(c.NAMELOOKUP_TIME),
        "connect_time": c.getinfo(c.CONNECT_TIME),
        "appconnect_time": c.getinfo(c.APPCONNECT_TIME),
        "pretransfer_time": c.getinfo(c.PRETRANSFER_TIME),
        "redirect_time": c.getinfo(c.REDIRECT_TIME),
        "redirect_count": c.getinfo(c.REDIRECT_COUNT),
        "size_upload": c.getinfo(c.SIZE_UPLOAD),
        "size_download": c.getinfo(c.SIZE_DOWNLOAD),
        "speed_download": c.getinfo(c.SPEED_DOWNLOAD),
        "speed_upload": c.getinfo(c.SPEED_UPLOAD),
        "header_size": c.getinfo(c.HEADER_SIZE),
        "request_size": c.getinfo(c.REQUEST_SIZE),
        "ssl_verifyresult": c.getinfo(c.SSL_VERIFYRESULT),
        "content_length_download": c.getinfo(c.CONTENT_LENGTH_DOWNLOAD),
        "content_type": c.getinfo(c.CONTENT_TYPE),
        "ssl_engines": c.getinfo(c.SSL_ENGINES),
        "ssl_verifyresult": c.getinfo(c.SSL_VERIFYRESULT),
        "http_auth_avail": c.getinfo(c.HTTPAUTH_AVAIL),
        "proxy_auth_avail": c.getinfo(c.PROXYAUTH_AVAIL),
        "os_errno": c.getinfo(c.OS_ERRNO),
        "num_connects": c.getinfo(c.NUM_CONNECTS),
        #        'ssl_session': c.getinfo(c.SSL_SESSION),
        "starttransfer_time": c.getinfo(c.STARTTRANSFER_TIME),
        "redirect_time": c.getinfo(c.REDIRECT_TIME),
        "redirect_url": c.getinfo(c.REDIRECT_URL),
    }


def status_code_description(status_code):
    """Looong list of http error codes and their descriptions"""
    descriptions = {
        100: "100 Continue: The server has received the request headers and the client should proceed to send the request body.",
        101: "101 Switching Protocols: The requester has asked the server to switch protocols.",
        102: "102 Processing: The server is processing the request.",
        103: "103 Early Hints: Used to return some response headers before final HTTP message.",
        200: "200 OK: The request has succeeded.",
        201: "201 Created: The request has been fulfilled and a new resource has been created.",
        202: "202 Accepted: The request has been accepted for processing, but the processing has not been completed.",
        203: "203 Non-Authoritative Information: The returned meta-information in the entity-header is not the definitive set as available from the origin server.",
        204: "204 No Content: The server has fulfilled the request but does not need to return an entity-body.",
        205: "205 Reset Content: The server has fulfilled the request and the user agent should reset the document view which caused the request to be sent.",
        206: "206 Partial Content: The server has fulfilled the partial GET request for the resource.",
        207: "207 Multi-Status: The message body that follows is an XML message and can contain a number of separate response codes.",
        208: "208 Already Reported: The members of a DAV binding have already been enumerated in a previous reply to this request, and are not being included again.",
        226: "226 IM Used: The server has fulfilled a request for the resource.",
        300: "300 Multiple Choices: The requested resource corresponds to any one of a set of representations.",
        301: "301 Moved Permanently: The requested resource has been assigned a new permanent URI.",
        302: "302 Found: The requested resource resides temporarily under a different URI.",
        303: "303 See Other: The response to the request can be found under a different URI.",
        304: "304 Not Modified: The requested resource has not been modified.",
        305: "305 Use Proxy: The requested resource must be accessed through the proxy given by the Location field.",
        306: "306 Switch Proxy: No longer used.",
        307: "307 Temporary Redirect: The requested resource resides temporarily under a different URI.",
        308: "308 Permanent Redirect: The requested resource has been assigned a new permanent URI.",
        400: "400 Bad Request: The request could not be understood by the server.",
        401: "401 Unauthorized: The request requires user authentication.",
        402: "402 Payment Required: This response code is reserved for future use.",
        403: "403 Forbidden: The server understood the request, but is refusing to fulfill it.",
        404: "404 Not Found: The server has not found anything matching the Request-URI.",
        405: "405 Method Not Allowed: The method specified in the Request-Line is not allowed for the resource identified by the Request-URI.",
        406: "406 Not Acceptable: The resource identified by the request is only capable of generating response entities which have content characteristics not acceptable according to the accept headers sent in the request.",
        407: "407 Proxy Authentication Required: This code is similar to 401 (Unauthorized), but indicates that the client must first authenticate itself with the proxy.",
        408: "408 Request Timeout: The client did not produce a request within the time that the server was prepared to wait",
        409: "409 Conflict: This response is sent when a request conflicts with the current state of the server.",
        410: "410 Gone: This response is sent when the requested content has been permanently deleted from server, with no forwarding address.",
        411: "411: Length Required: Server rejected the request because the Content-Length header field is not defined and the server requires it.",
        412: "412: Precondition Failed: The client has indicated preconditions in its headers which the server does not meet.",
        413: "413: Payload Too Large: Request entity is larger than limits defined by server. The server might close the connection or return an Retry-After header field.",
        414: "414: URI Too Long: The URI requested by the client is longer than the server is willing to interpret.",
        415: "415: Unsupported Media Type: The media format of the requested data is not supported by the server, so the server is rejecting the request.",
        416: "416: Range Not Satisfiable: The range specified by the Range header field in the request cannot be fulfilled. It's possible that the range is outside the size of the target URI's data.",
        417: "417: Expectation Failed: This response code means the expectation indicated by the Expect request header field cannot be met by the server.",
        418: "418: I'm a teapot: The server refuses the attempt to brew coffee with a teapot.",
        421: "421: Misdirected Request: The request was directed at a server that is not able to produce a response.",
        422: "422: Unprocessable Content (WebDAV): The request was well-formed but was unable to be followed due to semantic errors.",
        423: "423: Locked (WebDAV): The resource that is being accessed is locked.",
        424: "424: Failed Dependency (WebDAV): The request failed due to failure of a previous request.",
        425: "425: Too Early Experimental: Indicates that the server is unwilling to risk processing a request that might be replayed.",
        426: "426: Upgrade Required: The server refuses to perform the request using the current protocol but might be willing to do so after the client upgrades to a different protocol. The server sends an Upgrade header in a 426 response to indicate the required protocol(s).",
        428: "428: Precondition Required: The origin server requires the request to be conditional. This response is intended to prevent the 'lost update' problem, where a client GETs a resource's state, modifies it and PUTs it back to the server, when meanwhile a third party has modified the state on the server, leading to a conflict.",
        429: "429: Too Many Requests: The user has sent too many requests in a given amount of time ('rate limiting').",
        431: "431: Request Header Fields Too Large: The server is unwilling to process the request because its header fields are too large. The request may be resubmitted after reducing the size of the request header fields.",
        451: "451: Unavailable For Legal Reasons: The user agent requested a resource that cannot legally be provided, such as a web page censored by a government.",
        500: "500: Internal Server Error: The server has encountered a situation it does not know how to handle.",
        501: "501: Not Implemented: The request method is not supported by the server and cannot be handled. The only methods that servers are required to support (and therefore that must not return this code) are GET and HEAD.",
        502: "502: Bad Gateway: This error response means that the server, while working as a gateway to get a response needed to handle the request, got an invalid response.",
        503: "503: Service Unavailable: The server is not ready to handle the request. Common causes are a server that is down for maintenance or that is overloaded.",
        504: "504: Gateway Timeout: This error response is given when the server is acting as a gateway and cannot get a response in time.",
        505: "505: HTTP Version Not Supported: The HTTP version used in the request is not supported by the server.",
        506: "506: Variant Also Negotiates: The server has an internal configuration error: the chosen variant resource is configured to engage in transparent content negotiation itself, and is therefore not a proper end point in the negotiation process.",
        507: "507: Insufficient Storage (WebDAV): The method could not be performed on the resource because the server is unable to store the representation needed to successfully complete the request.",
        508: "508: Loop Detected (WebDAV): The server detected an infinite loop while processing the request.",
        510: "510: Not Extended: Further extensions to the request are required for the server to fulfill it.",
        511: "511: Network Authentication Required: Indicates that the client needs to authenticate.",
    }
    if status_code in descriptions:
        return descriptions[status_code]
    else:
        return f"Status code {status_code} not found."


def gurl(url, options={}, timeout=30):
    """Get a url with timeout and full error reporting"""
    buffer = BytesIO()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.FOLLOWLOCATION, True)

    for option, value in options.items():
        c.setopt(option, value)

    try:
        c.setopt(pycurl.TIMEOUT, timeout)
        c.perform()
        status_code = c.getinfo(pycurl.HTTP_CODE)
        if status_code == 200:
            return buffer.getvalue()
        else:
            raise ValueError(
                f"Request failed with status code {status_code}\n{status_code_description(status_code)}\n{cinfo(c)}"
            )
    except pycurl.error as e:
        raise ValueError(f"Request failed with error {e}")
