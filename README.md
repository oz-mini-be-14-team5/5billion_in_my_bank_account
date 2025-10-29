# 통장잔고 5조팀

### http://deardiary.p-e.kr/

## 기본적인 폴더구조

### 루트폴더
- /src - 파이썬 소스코드
- /data - 스크래핑한 rawdata
- /storage - 기본 이미지 저장 스토리지
- /design - 페이지 목업 이미지
- /scraping - 스크래핑 툴
- main.py - 프로그램 엔트리
### /src
- /model - orm 모델
- /model/schema - pydantic 모델
- /router - 모든 라우터들
- /static - 모든 스테틱 파일들
- /tools - 특정 기능의 함수들
### /src/static
- /asset - 이미지, .js , .css 등
- /html - .html 파일들
- /response - 404 페이지 등 서버권위적인 파일들

## 추가 기획
기존 가이드라인에서 벗어나 추가적인 기획을 하여 구현하였습니다.  

- ### jwt_blcaklist 구현 X
  stateless를 위해 jwt를 사용하는것.  
  jwt_blacklist를 관리하고 대조 작업을 하면 세션에 비해 이점이 없다고 판단, 과감히 미구현.

- ### AUTH0 ?
  docs에서 맨날 토큰 복붙 귀찮아서 바로 docs에서 아이디 비번으로 로그인이 가능하게 구현.
  username을 login_id에 대응하여 구현함.

[추가된 API들]
- ### [GET] users/calander
  current_user의 모든 post의 date , 해당 일에 작성된 post의 id들을 반환.  

- ### [GET] posts/by-week/?target_date
  target_date가 해당하는 주의 유저가 작성한 posts 들을 반환.  

- ### [GET] posts/{post_id}/image
  해당 post의 author가 현재 접속한 유저라면 이미지를 가져옴.  

- ### [POST] posts/{post_id}/image
  해당 post의 author가 현재 접속한 유저라면 이미지를 가져옴.

- ### 정적 라우팅
  prefix가 없다면 기본적으로 html폴더의 경로를 통해 반환. 경로를 적지 않을시 index.html을 전송.  
  404 에러페이지같은 상대경로가 아닌 서버가 직접 반환해야하는 response가 필요하다면 페이지를 필요로 한다면 static/response를 통해 반환.  
  /ast/ 라우팅으로 static/asset 안의 폴더를 탐색하여 반환.  
  기능은 구현하였지만 api 위주의 단일페이지로 구성하게 되었음.  



## 프론트

열심히 목업이미지 만들었는데 그냥 시간부족으로 gpt 돌렸음

아래는 열심히 만든 목업이미지

### 로그인 화면
![img2](/design/not_authed_page.png)

### 앱 화면
![img1](/design/authed_page.png)




