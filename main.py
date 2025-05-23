from recommender import recommend_travel_places

if __name__ == "__main__":
    user_input = input("여행 스타일, 인원수, 일정 등을 입력하세요: ")
    csv_path = "data/busan_spots.csv"

    recommendations = recommend_travel_places(user_input, csv_path)
    print("추천 여행지:")
    print(recommendations)