# httpclientjk
----

## http client 설계
---
### requests package  
#### requests.get(url, request\_header\_dict)  return:: status\_line, response\_header\_dict, contents  

url과 필요시 request header dictionary를 퍼래미터로 받으면  
해당 url의 웹 서버로 http GET request를 날린다.  

웹 서버로 TCP 연결을 위해 socket 패키지를 이용한다.  
본 클라이언트에서 socket을 생성해서  
connection을 얻은 다음  

request message를 웹 서버로 전송한다.  

request message를 날릴 때,  
1. Request Line  
2. CRLF  
3. Request Headers  
4. CRLF CRLF  
의 형태로 Request message를 형성한 후에  
socket 통신을 통해 웹 서버로 request message를 전송한다.  

- 전송 후 서버로 부터 request response가 오는데, 이를 recv한 후에,  
  - Status Line의 Status code를 판단후 3xx가 아니라면  
    - Response Headers와 Response Body를 포멧팅 후 return 한다.  
  - Status Line의 Status code가 3xx라면,  
    - Location의 url로 get을 다시 요청한다.
      - return된 Status Code가 3xx가 아니라면
        - Response Headers와 Response Body를 포멧팅 후 return 한다.
      - Status Code가 3xx라면
        - 3xx가 아닐때까지 계속 get을 요청한다.  

#### request.post(url, body, request\_header\_dict, request\_body\_dict)  return::  status\_line, response\_header\_dict, contents
url과 body, request header dictionary를 퍼래미터로 받으면  
해당 url의 웹 서버로 http POST request를 날린다.  

웹 서버로 TCP 연결을 위해 socket 패키지를 이용한다.  
본 클라이언트에서 socket을 생성해서  
connection을 얻은 다음  

request message를 웹 서버로 전송한다.  

request message를 날릴 때,  
1. Request Line  
2. CRLF  
3. Request Header  
4. CRLF CRLF  
6. body  
7. CRLF  
의 형태로 Request message를 형성한 후에  
socket 통신을 통해 웹 서버로 request message를 전송한다.  

- 전송 후 서버로 부터 request response가 오는데, 이를 recv한 후에,  
  - Status Line의 Status code를 판단후 3xx가 아니라면  
    - Response Headers와 Response Body를 포멧팅 후 return 한다.  
  - Status Line의 Status code가 3xx라면,  
    - Location의 url로 get을 다시 요청한다.
      - return된 Status Code가 3xx가 아니라면
        - Response Headers와 Response Body를 포멧팅 후 return 한다.
      - Status Code가 3xx라면
        - 3xx가 아닐때까지 계속 get을 요청한다.