from fastapi import FastAPI
from datetime import datetime, timedelta
import json
import os

app = FastAPI(title="Go to Church Picker", version="1.0")

# Load timetable data once
BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "data/goto_church_timetable.json"), encoding="utf-8") as f:
    timetable = json.load(f)

def get_next_departures(now, timetable, offset=0, count=3):
    """현재 시각 + offset 기준 이후의 열차 N개 반환"""
    ref_time = (now + timedelta(minutes=offset)).strftime("%H:%M")
    future = [t for t in timetable if t > ref_time]
    return future[:count] if future else ["(다음 운행 없음)"]

@app.get("/gotochurch")
def gotochurch(now: str | None = None):
    """현재 시각 기준으로 두 루트별 다음 열차 3개 반환 (루트별 처리 함수 사용)"""
    now_dt = datetime.strptime(now, "%H:%M") if now else datetime.now()

    # 루트 전용 함수에서 데이터를 생성하도록 위임
    route1_data = get_route1_data(now_dt)
    route2_data = get_route2_data(now_dt)

    # 추천 로직: 두 루트의 옵션들을 최종 도착 시간 기준으로 정렬해서 추천
    def get_final_arrival_time(route_data, option_index):
        """각 옵션의 최종 도착 시간을 datetime으로 반환"""
        option = route_data["next"][option_index]
        if route_data["name"].startswith("백석"):  # route1
            arrival_str = option["둔촌동역 도착시간"]
            # 출발 시간 기준으로 날짜 설정 (환승으로 인해)
            departure_time = datetime.strptime(option["백석역 출발"], "%H:%M").replace(
                year=now_dt.year, month=now_dt.month, day=now_dt.day
            )
            if departure_time < now_dt:
                departure_time += timedelta(days=1)
            arrival_time = datetime.strptime(arrival_str, "%H:%M").replace(
                year=departure_time.year, month=departure_time.month, day=departure_time.day
            )
            # 환승 대기나 지연으로 다음 날 가능성 고려
            if arrival_time < departure_time:
                arrival_time += timedelta(days=1)
            return arrival_time
        else:  # route2
            arrival_str = option["종합운동장역 도착"]
            departure_time = datetime.strptime(option["당산역 급행출발"], "%H:%M").replace(
                year=now_dt.year, month=now_dt.month, day=now_dt.day
            )
            if departure_time < now_dt:
                departure_time += timedelta(days=1)
            arrival_time = datetime.strptime(arrival_str, "%H:%M").replace(
                year=departure_time.year, month=departure_time.month, day=departure_time.day
            )
            return arrival_time
    
    # route1과 route2의 모든 옵션에 대해 최종 도착 시간 계산
    route1_options = []
    for i in range(len(route1_data["next"])):
        arrival_time = get_final_arrival_time(route1_data, i)
        route1_options.append({
            "route": "route1",
            "option": i,
            "arrival_time": arrival_time,
            "details": route1_data["next"][i]
        })
    
    route2_options = []
    for i in range(len(route2_data["next"])):
        arrival_time = get_final_arrival_time(route2_data, i)
        route2_options.append({
            "route": "route2",
            "option": i,
            "arrival_time": arrival_time,
            "details": route2_data["next"][i]
        })
    
    # 모든 옵션을 합쳐 도착 시간으로 정렬
    all_options = route1_options + route2_options
    all_options.sort(key=lambda x: x["arrival_time"])
    
    return {
        "timestamp": now_dt.strftime("%H:%M"),
        "routes": {
            "route1": route1_data,
            "route2": route2_data
        },
        "recommendations": [
            {
                "rank": i+1,
                "route": opt["route"],
                "option_index": opt["option"],
                "arrival_time": opt["arrival_time"].strftime("%H:%M"),
                "details": opt["details"]
            }
            for i, opt in enumerate(all_options)
        ]
    }

def get_route1_data(now_dt):
    """route1-1 전용 데이터 생성 함수 (사용자가 수정 가능)"""
    next_departures = get_next_departures(now_dt, timetable["route1-1"]["departures"])
    # next_transfers must be computed from the first departure time; ensure we have valid departures first

    # 문자열을 datetime으로 변환
    first_departure_time = datetime.strptime(next_departures[0], "%H:%M")
    # 종로3가 도착시간(offset 42분)기준으로 환승열차(5호선) 2개의 열차를 뽑기.
    # (후속 조합을 위해 여러 환승 시간을 미리 확보)
    next_transfers_from_first = get_next_departures(first_departure_time, timetable["route1-2"]["transfers"], offset=42, count=2)

    second_departure_time = datetime.strptime(next_departures[1], "%H:%M")
    # 종로3가 도착시간(offset 42분)기준으로 환승열차(5호선) 2개의 열차를 뽑기.
    # (후속 조합을 위해 여러 환승 시간을 미리 확보)
    next_transfers_from_second = get_next_departures(second_departure_time, timetable["route1-2"]["transfers"], offset=42, count=2)

    third_departure_time = datetime.strptime(next_departures[2], "%H:%M")
    # 종로3가 도착시간(offset 42분)기준으로 환승열차(5호선) 2개의 열차를 뽑기.
    # (후속 조합을 위해 여러 환승 시간을 미리 확보)
    next_transfers_from_third = get_next_departures(third_departure_time, timetable["route1-2"]["transfers"], offset=42, count=2)

    # 종로3가역 도착시간 계산: 출발시간 + 42분
    def calculate_jongno3ga_arrival(departure_time):
        """출발시간 + 42분(종로3가 도착) 시간을 문자열로 반환"""
        arrival_time = departure_time + timedelta(minutes=42)
        return arrival_time.strftime("%H:%M")
    
    # 환승시간 계산: 종로3가 도착시간(출발시간 + 42분)과 환승열차 시간의 차이
    def calculate_transfer_time(departure_time, transfer_time_str):
        """출발시간 + 42분(종로3가 도착)과 환승열차 시간의 차이를 분 단위로 계산"""
        arrival_at_jongno3ga = departure_time + timedelta(minutes=42)
        transfer_time = datetime.strptime(transfer_time_str, "%H:%M")
        # 같은 날짜로 설정
        transfer_time = transfer_time.replace(
            year=arrival_at_jongno3ga.year,
            month=arrival_at_jongno3ga.month,
            day=arrival_at_jongno3ga.day
        )
        # 환승 시간이 종로3가 도착 시간보다 이전이면 다음 날로 간주
        if transfer_time < arrival_at_jongno3ga:
            transfer_time += timedelta(days=1)
        diff = transfer_time - arrival_at_jongno3ga
        return int(diff.total_seconds() / 60)
    
    # 도착시간 계산: 환승열차 시간 + 32분
    def calculate_arrival_time(transfer_time_str):
        """환승열차 시간에 32분을 더한 도착시간 반환"""
        transfer_time = datetime.strptime(transfer_time_str, "%H:%M")
        arrival_time = transfer_time + timedelta(minutes=32)
        return arrival_time.strftime("%H:%M")
    
    # 첫 번째 출발열차의 환승시간 계산
    transfer_time_first = [
        calculate_transfer_time(first_departure_time, next_transfers_from_first[0]),
        calculate_transfer_time(first_departure_time, next_transfers_from_first[1])
    ]
    
    # 두 번째 출발열차의 환승시간 계산
    transfer_time_second = [
        calculate_transfer_time(second_departure_time, next_transfers_from_second[0]),
        calculate_transfer_time(second_departure_time, next_transfers_from_second[1])
    ]
    
    # 세 번째 출발열차의 환승시간 계산
    transfer_time_third = [
        calculate_transfer_time(third_departure_time, next_transfers_from_third[0]),
        calculate_transfer_time(third_departure_time, next_transfers_from_third[1])
    ]
    
    # 도착시간 계산
    arrival_time_first = [
        calculate_arrival_time(next_transfers_from_first[0]),
        calculate_arrival_time(next_transfers_from_first[1])
    ]
    arrival_time_second = [
        calculate_arrival_time(next_transfers_from_second[0]),
        calculate_arrival_time(next_transfers_from_second[1])
    ]
    arrival_time_third = [
        calculate_arrival_time(next_transfers_from_third[0]),
        calculate_arrival_time(next_transfers_from_third[1])
    ]

    # 조합 데이터 생성 (출발시간, 환승시간, 환승대기시간, 도착시간 포함)
    
    def calculate_time_to_station(departure_time_str):
        """현재 시각부터 출발 시간까지의 차이(분) 계산"""
        departure_time = datetime.strptime(departure_time_str, "%H:%M").replace(
            year=now_dt.year, month=now_dt.month, day=now_dt.day
        )
        if departure_time < now_dt:
            departure_time += timedelta(days=1)
        diff = (departure_time - now_dt).total_seconds() / 60
        return int(diff)
    
    가장빠른열차_제1조합 = {
        "역까지 가는 시간": calculate_time_to_station(next_departures[0]),
        "백석역 출발": next_departures[0],
        "종로3가역 도착": calculate_jongno3ga_arrival(first_departure_time),
        "환승 사이시간": transfer_time_first[0],
        "종로3가역 출발": next_transfers_from_first[0],
        "둔촌동역 도착시간": arrival_time_first[0]
    }
    가장빠른열차_제2조합 = {
        "역까지 가는 시간": calculate_time_to_station(next_departures[0]),
        "백석역 출발": next_departures[0],
        "종로3가역 도착": calculate_jongno3ga_arrival(first_departure_time),
        "환승 사이시간": transfer_time_first[1],
        "종로3가역 출발": next_transfers_from_first[1],
        "둔촌동역 도착시간": arrival_time_first[1]
    }
    두번째열차_제1조합 = {
        "역까지 가는 시간": calculate_time_to_station(next_departures[1]),
        "백석역 출발": next_departures[1],
        "종로3가역 도착": calculate_jongno3ga_arrival(second_departure_time),
        "환승 사이시간": transfer_time_second[0],
        "종로3가역 출발": next_transfers_from_second[0],
        "둔촌동역 도착시간": arrival_time_second[0]
    }
    두번째열차_제2조합 = {
        "역까지 가는 시간": calculate_time_to_station(next_departures[1]),
        "백석역 출발": next_departures[1],
        "종로3가역 도착": calculate_jongno3ga_arrival(second_departure_time),
        "환승 사이시간": transfer_time_second[1],
        "종로3가역 출발": next_transfers_from_second[1],
        "둔촌동역 도착시간": arrival_time_second[1]
    }
    세번째열차_제1조합 = {
        "역까지 가는 시간": calculate_time_to_station(next_departures[2]),
        "백석역 출발": next_departures[2],
        "종로3가역 도착": calculate_jongno3ga_arrival(third_departure_time),
        "환승 사이시간": transfer_time_third[0],
        "종로3가역 출발": next_transfers_from_third[0],
        "둔촌동역 도착시간": arrival_time_third[0]
    }
    세번째열차_제2조합 = {
        "역까지 가는 시간": calculate_time_to_station(next_departures[2]),
        "백석역 출발": next_departures[2],
        "종로3가역 도착": calculate_jongno3ga_arrival(third_departure_time),
        "환승 사이시간": transfer_time_third[1],
        "종로3가역 출발": next_transfers_from_third[1],
        "둔촌동역 도착시간": arrival_time_third[1]
    }
    결과물 = [
        가장빠른열차_제1조합,
        가장빠른열차_제2조합,
        두번째열차_제1조합,
        두번째열차_제2조합,
        세번째열차_제1조합,
        세번째열차_제2조합
    ]
    return {
        "name": "백석->종로3가->둔촌동역",
        "next": 결과물
    }

def get_route2_data(now_dt):
    """route2 전용 데이터 생성 함수 (사용자가 수정 가능)"""
    # 현재 시각 + 45분 이후의 열차 3개 가져오기
    next_trains = get_next_departures(now_dt, timetable["route2"]["express_train"], offset=45, count=3)
    
    # 각 열차와 현재 시각의 차이(분) 계산
    def calculate_time_diff(departure_time_str):
        """출발 시간과 현재 시각의 차이를 분 단위로 계산"""
        departure_time = datetime.strptime(departure_time_str, "%H:%M")
        # 같은 날짜로 설정
        departure_time = departure_time.replace(
            year=now_dt.year,
            month=now_dt.month,
            day=now_dt.day
        )
        # 출발 시간이 현재 시각보다 이전이면 다음 날로 간주
        if departure_time < now_dt:
            departure_time += timedelta(days=1)
        diff = departure_time - now_dt
        return int(diff.total_seconds() / 60)
    
    # 도착시간 계산: 출발시간 + 34분
    def calculate_arrival_time(departure_time_str):
        """출발 시간에 34분을 더한 도착시간 반환"""
        departure_time = datetime.strptime(departure_time_str, "%H:%M")
        arrival_time = departure_time + timedelta(minutes=34)
        return arrival_time.strftime("%H:%M")
    
    # 결과 데이터 생성
    결과물 = []
    for train_time in next_trains:
        if train_time != "(다음 운행 없음)":
            time_diff = calculate_time_diff(train_time)
            결과물.append({
                "버스타러가는 시간 + 버스가 당산까지 가는 시간": time_diff,
                "당산역 급행출발": train_time,
                "종합운동장역 도착": calculate_arrival_time(train_time)
            })
    
    return {
        "name": timetable["route2"]["name"],
        "next": 결과물
    }
