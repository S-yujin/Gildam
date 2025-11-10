from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta

class RouteOptimizer:
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """두 지점 간 거리 계산 (km)"""
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    @staticmethod
    def optimize_route_with_time(places):
        """
        시간순 정렬 + 지리적 최적화
        식사 시간대는 고정, 나머지는 동선 최적화
        """
        if len(places) <= 2:
            return places
        
        # 식당/카페는 시간대별로 고정
        meal_times = []
        flexible_places = []
        
        for place in places:
            if place['category'] in ['식당', '카페']:
                meal_times.append(place)
            else:
                flexible_places.append(place)
        
        # 식사 시간 기준으로 정렬
        meal_times.sort(key=lambda x: x['start_time'])
        
        # 유연한 장소들은 가까운 순서로 재배치
        if flexible_places:
            optimized_flexible = [flexible_places[0]]
            remaining = flexible_places[1:]
            
            while remaining:
                last = optimized_flexible[-1]
                nearest = min(
                    remaining,
                    key=lambda p: RouteOptimizer.haversine_distance(
                        last['latitude'], last['longitude'],
                        p['latitude'], p['longitude']
                    )
                )
                optimized_flexible.append(nearest)
                remaining.remove(nearest)
            
            flexible_places = optimized_flexible
        
        # 시간대별로 병합
        result = []
        flex_idx = 0
        
        for meal in meal_times:
            meal_time = datetime.strptime(meal['start_time'], '%H:%M')
            
            # 식사 전에 올 수 있는 관광지들 추가
            while flex_idx < len(flexible_places):
                place = flexible_places[flex_idx]
                place_time = datetime.strptime(place['start_time'], '%H:%M')
                
                if place_time < meal_time:
                    result.append(place)
                    flex_idx += 1
                else:
                    break
            
            result.append(meal)
        
        # 남은 관광지들 추가
        result.extend(flexible_places[flex_idx:])
        
        return result
    
    @staticmethod
    def calculate_travel_time(lat1, lon1, lat2, lon2):
        """이동 시간 계산 (분) - 교통 상황 고려"""
        distance = RouteOptimizer.haversine_distance(lat1, lon1, lat2, lon2)
        
        # 거리별 평균 속도 (부산 시내 기준)
        if distance < 2:
            speed = 15  # 도보 가능
        elif distance < 5:
            speed = 25  # 시내 버스/택시
            return int((distance / speed) * 60) + 10  # 대기시간 +10분
        else:
            speed = 35  # 시외/지하철
            return int((distance / speed) * 60) + 15  # 대기시간 +15분
        
        return int((distance / speed) * 60)
    
    @staticmethod
    def add_travel_times(places):
        """장소 간 이동 시간 추가"""
        for i in range(len(places) - 1):
            current = places[i]
            next_place = places[i + 1]
            
            travel_time = RouteOptimizer.calculate_travel_time(
                current['latitude'], current['longitude'],
                next_place['latitude'], next_place['longitude']
            )
            
            places[i]['travel_to_next'] = travel_time
            places[i]['travel_distance'] = round(
                RouteOptimizer.haversine_distance(
                    current['latitude'], current['longitude'],
                    next_place['latitude'], next_place['longitude']
                ), 2
            )
        
        return places