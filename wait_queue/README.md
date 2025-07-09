# FastAPI Wait Queue Example

## 소개
 FastAPI, Redis, WebSocket을 활용한 대기열(Wait Queue) 시스템 예제입니다.
- 사용자는 `/token/` 엔드포인트에서 토큰을 발급받고,
- `/ws/` WebSocket에 토큰으로 접속하면 대기열 위치를 실시간으로 안내받습니다.
- 입장 가능 인원이 생기면 자동으로 알림을 받고, active 상태로 승격됩니다.

## 주요 기능
- **토큰 발급**: REST API로 대기 토큰 발급
- **대기열 관리**: Redis 기반 FIFO 큐
- **WebSocket 실시간 알림**: 대기순번, 입장 가능 알림
- **자동 승격**: 자리가 나면 대기자 자동 입장

## 실행 방법

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **Redis 실행**
   - 로컬 또는 Docker로 Redis를 실행하세요.
   - 예시(docker-compose):
     ```bash
     docker-compose up -d
     ```

3. **FastAPI 서버 실행**
   ```bash
   uvicorn main:app --reload
   ```

4. **토큰 발급**
   ```http
   POST /token/
   ```
   - 응답: `{ "uuid": "...", "status": "wait" }`

5. **WebSocket 연결**
   - 클라이언트에서 `/ws/`로 WebSocket 연결 후, 아래와 같이 토큰을 전송:
     ```json
     { "uuid": "<발급받은 uuid>",
        "status": "wait"
      }

     ```
   - 서버로부터 대기순번, 입장 알림을 실시간으로 받음

## 테스트
- tests에서 pytest 구현 (유닛 테스트, 통합 테스트)

- locustfile.py 에서 부하테스트 구현.

## 폴더 구조

```
wait_queue/
    api/         # FastAPI 라우터
    model/       # 데이터 모델
    repository/  # Redis 싱글톤/저장소
    service/     # 대기열, active 관리, 모니터, 옵저버 서비스 로직.
    utils/       # 설정, 로거
    tests/       # 통합/단위 테스트
    docker-compose.yml
    requirements.txt
    main.py
```

#### 참고
- Redis의 keyspace notification(`notify-keyspace-events Ex`)을 사용하므로, Redis 설정 필요



## 추가기능: rate limiter 구현

api 콜 제한 알고리즘 
- fixed_window
- sliding window
- token bucket

tests\integration\test_limiter.py   
fixed_window 테스트 내용  
- rate limit: 5 회 / 10초  
- 테스트 인원: 3명  
- 시나리오: 
   - 5회 허용 200
   - 6번째 거부 429
   - 윈도우 10초 대기 
   - 재허용 200
테스트 결과  

<details>
<summary>상세 로그</summary>

```
338436b4-01ad-4ce3-83e3-74e537ccb628
<Response [200 OK]>
<Response [200 OK]>
<Response [200 OK]>
<Response [200 OK]>
<Response [200 OK]>
<Response [429 Too Many Requests]>
sleeping for window length 10
after window
<Response [200 OK]>


543903c4-4823-4381-a36a-28411ca394d7
<Response [200 OK]>
<Response [200 OK]>
<Response [200 OK]>
<Response [200 OK]>
<Response [200 OK]>
<Response [429 Too Many Requests]>
sleeping for window length 10
after window
<Response [200 OK]>


6a11a54e-eaf3-4fbf-8d67-64cbd98bac38
<Response [200 OK]>
<Response [200 OK]>
<Response [200 OK]>
<Response [200 OK]>
<Response [200 OK]>
<Response [429 Too Many Requests]>
sleeping for window length 10
after window
<Response [200 OK]>
```

</details>