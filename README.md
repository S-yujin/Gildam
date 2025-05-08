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
- [ ] 부울경 ICT 신청하기
- [ ] 학습시킬 자료 수집 (SNS, 공공데이터 등)
  - [ ] 부
  - [ ] 울
  - [ ] 경
      
