# Gildom

참여 공모전: [부산테크노파크 Big Data 활용 대회](https://www.dxchallenge.co.kr/events/bigdataanalysis2025)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[부울경 ICT 아이디어 경진대회](https://www.busan.go.kr/nbnews/1679766)

### 주제: 길 위의 부산 이야기 (부산 여행 중 지역에 대한 스토리를 자동으로 작성하는 앱 개발)
이유: 대부분의 여행 지역이나 앱은 타인의 블로그나 SNS에 의존함.   
기술: LLM과 공공/민간 데이터를 이용하여 지역에 볼 수 있는 명소 및 볼거리를 알려줌. 

      
데이터셋: 
  - 부산광역시_부산명소정보 서비스 (제목, 부제목)
  - 부산광역시_부산축제정보 서비스
  - 부산광역시_명소 서비스(SHP): 지리정보 등록
  - 나머지 명소 데이터 셋 등등
   
프로그램:
  - Streamlit/ Dash 둘 중 선택
  - Openstreermap
  - GPT4, Deepseek, llama
  - Huggingface
       
프로그램 구조 설계:
  - Model - pydantic
  - View
  - Controller
      - Class StoryBuilder
   

## 할 일
- [x] 부울경 ICT 신청하기 (지역아이디어 부문)
- [ ] 학습시킬 자료 수집 (SNS, 공공데이터 등)
  - [x] 부
  - [ ] 울
  - [ ] 경
- [x] 비슷한 앱, 사이트 찾아보기
- [x] 체크박스 선택 후 다음 버튼을 눌르면 지도에 맵핑
- [ ] 지도 눈에 잘 들어오게 만들기
- [ ] 이동경로를 여러가지?로 추천?
- [ ] 이동경로 선텍 후 스토리 생성
- [ ] 이동경로에 따른 맛집, 카페, 숙박시설 등? 추천
- [ ] 여행 후 블로그, 티스토리, 밴드에 공유할 스토리형 여행 기록 생성
- [ ] ui 예쁘게 꾸미기.
- [ ] 속도 최적화
