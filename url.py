from fastapi import APIRouter
from fastapi.responses import JSONResponse
from firebase_admin import messaging

from transport.shuttle.get_info import get_departure_info, get_first_last_departure
from transport.shuttle.date import is_semester, which_weekday
from transport.bus.get_arrival_info import get_bus_info, get_bus_timetable, get_realtime_departure
from transport.subway.get_info import get_subway_info, get_subway_timetable

from library.reading_room import get_reading_room_seat

from food.menu import CafeteriaSeoul, CafeteriaERICA, get_recipe, get_recipe_all_cafeteria

from app.common.models import ShuttleRequest, CampusRequest, BusRequest, MenuRequest, LanguageRequest

hanyang_app_router = APIRouter()


@hanyang_app_router.get('/shuttle')
async def get_shuttle_all_stop():
    """Get Departure Info for all bus stop"""
    result = {}
    bus_stop_list = ['Residence', 'Shuttlecock_O', 'Subway', 'YesulIn', 'Shuttlecock_I']
    for bus_stop in bus_stop_list:
        bus_to_come_dh, bus_to_come_dy, bus_to_come_c, _ = get_departure_info(path=bus_stop)
        result[bus_stop] = {"DH": [x.strftime("%H:%M") for x in bus_to_come_dh],
                            "DY": [x.strftime("%H:%M") for x in bus_to_come_dy],
                            "C": [x.strftime("%H:%M") for x in bus_to_come_c]}
    return JSONResponse(result)


@hanyang_app_router.post('/shuttle')
async def get_shuttle_stop(request: ShuttleRequest):
    """Get Departure Info for specific bus stop"""
    bus_stop = request.busStop
    bus_to_come_dh, bus_to_come_dy, bus_to_come_c, _ = get_departure_info(path=bus_stop)
    result = {"DH": [x.strftime("%H:%M") for x in bus_to_come_dh], "DY": [x.strftime("%H:%M") for x in bus_to_come_dy],
              "C": [x.strftime("%H:%M") for x in bus_to_come_c]}
    return JSONResponse(result)


@hanyang_app_router.post('/shuttle/by-stop')
async def get_shuttle_stop(request: ShuttleRequest):
    """Get Departure Info for specific bus stop"""
    bus_stop = request.busStop
    _, _, bus_info_dh, bus_info_dy, bus_info_c = get_first_last_departure(path=bus_stop)
    first_last_info = {"DH": [x.strftime("%H:%M") for x in bus_info_dh],
                       "DY": [x.strftime("%H:%M") for x in bus_info_dy], "C": [x.strftime("%H:%M") for x in bus_info_c]}

    bus_to_come_dh_week, bus_to_come_dy_week, bus_to_come_c_week, _ = get_departure_info(path=bus_stop, get_all=True,
                                                                                         fixed_date="week")
    bus_to_come_dh_weekend, bus_to_come_dy_weekend, bus_to_come_c_weekend, _ = get_departure_info(path=bus_stop,
                                                                                                  get_all=True,
                                                                                                  fixed_date="weekend")
    stop_view = {"Shuttlecock_I": "http://kko.to/TyWyjU3Yp", "Subway": "http://kko.to/c93C0UFYj",
                 "Residence": "http://kko.to/R-l1jU3DT", "YesulIn": "http://kko.to/7mzoYUFY0",
                 "Shuttlecock_O": "http://kko.to/v-3DYI3YM"}

    result = {"location": "", "roadView": stop_view[bus_stop], "first_last": first_last_info, "day": which_weekday(),
              "weekdays": {"DH": [x.strftime("%H:%M") for x in bus_to_come_dh_week],
                           "DY": [x.strftime("%H:%M") for x in bus_to_come_dy_week],
                           "C": [x.strftime("%H:%M") for x in bus_to_come_c_week]},
              "weekends": {"DH": [x.strftime("%H:%M") for x in bus_to_come_dh_weekend],
                           "DY": [x.strftime("%H:%M") for x in bus_to_come_dy_weekend],
                           "C": [x.strftime("%H:%M") for x in bus_to_come_c_weekend]},
              }
    return JSONResponse(result)


@hanyang_app_router.post('/subway')
async def get_subway(request: CampusRequest):
    """Get Departure Info for specific campus"""
    _, is_weekend = is_semester()
    is_weekend = True if is_weekend == 'weekend' else False
    campus = request.campus == "Seoul"

    if campus:
        response = {"Line2": get_subway_info(campus)}
    else:
        response = {"line4": get_subway_info(campus), "lineSuin": {
            "up": [{"terminalStn": x["endStn"], "time": x["time"].strftime("%H:%M")} for x in
                   get_subway_timetable(is_weekend)['up']],
            "down": [{"terminalStn": x["endStn"], "time": x["time"].strftime("%H:%M")} for x in
                     get_subway_timetable(is_weekend)['down']]}}

    return JSONResponse(response)


@hanyang_app_router.post('/bus')
async def get_bus_info_list(request: CampusRequest):
    _, is_weekend = is_semester()
    is_weekend = True if is_weekend == 'weekend' else False
    campus = request.campus == "Seoul"

    if campus:
        return JSONResponse({})
    else:
        return JSONResponse({"realtime": get_bus_info(), "timetable": {
            "10-1": [{"time": x["time"].strftime("%H:%M")} for x in get_bus_timetable(is_weekend)["10-1"]],
            "3102": [{"time": x["time"].strftime("%H:%M")} for x in get_bus_timetable(is_weekend)["3102"]]}})


@hanyang_app_router.post('/bus/by-route')
async def get_bus_info_by_route(request: BusRequest):
    _, is_weekend = is_semester()
    is_weekend = True if is_weekend == 'weekend' else False
    campus = request.campus == "Seoul"

    guest_house_stop = '216000379'
    main_gate_stop = '216000719'
    line_10_1 = '216000068'
    line_3102 = '216000061'
    line_707_1 = '216000070'

    if campus:
        return JSONResponse({})
    else:
        if request.route == "10-1":
            return JSONResponse({"realtime": get_realtime_departure(guest_house_stop, line_10_1),
                                 "timetable": [{"time": x["time"].strftime("%H:%M")} for x in
                                               get_bus_timetable(is_weekend, "10-1")]})
        elif request.route == "3102":
            return JSONResponse({"realtime": get_realtime_departure(guest_house_stop, line_3102),
                                 "timetable": [{"time": x["time"].strftime("%H:%M")} for x in
                                               get_bus_timetable(is_weekend, "3102")]})
        else:
            return JSONResponse({"realtime": get_realtime_departure(main_gate_stop, line_707_1),
                                 "timetable": []})


@hanyang_app_router.post('/bus/timetable')
async def get_bus_info_by_route(request: BusRequest):
    _, is_weekend = is_semester()
    is_weekend = True if is_weekend == 'weekend' else False
    campus = request.campus == "Seoul"

    guest_house_stop = '216000379'
    main_gate_stop = '216000719'
    line_10_1 = '216000068'
    line_3102 = '216000061'
    line_707_1 = '216000070'

    if campus:
        return JSONResponse({})
    else:
        if request.route == "10-1":
            data = get_bus_timetable(is_weekend, "10-1", get_all=True)
            return JSONResponse({
                "weekdays": [{"time": x["time"].strftime("%H:%M")} for x in data["weekdays"]],
                "saturday": [{"time": x["time"].strftime("%H:%M")} for x in data["sat"]],
                "sunday": [{"time": x["time"].strftime("%H:%M")} for x in data["sun"]],
            })
        elif request.route == "3102":
            data = get_bus_timetable(is_weekend, "3102", get_all=True)
            return JSONResponse({
                "weekdays": [{"time": x["time"].strftime("%H:%M")} for x in data["weekdays"]],
                "saturday": [{"time": x["time"].strftime("%H:%M")} for x in data["sat"]],
                "sunday": [{"time": x["time"].strftime("%H:%M")} for x in data["sun"]],
            })


@hanyang_app_router.post('/library')
async def get_library_list(request: CampusRequest):
    campus = request.campus == "Seoul"
    response = {}
    for x in get_reading_room_seat(campus=campus)[0]:
        if "미개방" not in x['name'] and x['activeTotal'] > 0:
            response[x['name']] = {'active': x['activeTotal'], 'occupied': x['occupied'], 'available': x['available']}

    return JSONResponse(response)


@hanyang_app_router.get('/library')
async def get_library_list():
    response = {}
    for x in get_reading_room_seat(campus=0)[0]:
        if "미개방" not in x['name'] and x['activeTotal']:
            response[x['name']] = {'active': x['activeTotal'], 'occupied': x['occupied'], 'available': x['available']}

    rooms = {"제1열람실": "reading_room_1", "제2열람실": "reading_room_2", "제3열람실": "reading_room_3", "제4열람실": "reading_room_4"}
    for name, room in response.items():
        if room['available'] > 0:
            for language in ["ko_KR", "en_US", "zh"]:
                topic = f"{rooms[name]}.{language}"
                # See documentation on defining a message payload.
                message = messaging.Message(
                    data={'type': 'reading_room', 'name': topic.split(".")[0], "language": language.split("_")[0]},
                    topic=topic,
                    android=messaging.AndroidConfig(priority="high")
                )
                messaging.send(message)
    return ''


@hanyang_app_router.post('/food/by-restaurant')
async def get_food_menu(request: MenuRequest):
    campus = request.campus == "Seoul"
    if campus:
        restaurant_list = {"student_1": CafeteriaSeoul.student_seoul_1, "student_2": CafeteriaSeoul.student_seoul_2,
                           "teacher_1": CafeteriaSeoul.teacher_seoul_1, "teacher_2": CafeteriaSeoul.teacher_seoul_2,
                           "dormitory_1": CafeteriaSeoul.dorm_seoul_1, "dormitory_2": CafeteriaSeoul.dorm_seoul_2,
                           "hangwon": CafeteriaSeoul.hangwon_seoul, "sarang": CafeteriaSeoul.sarang_seoul}
    else:
        restaurant_list = {"student": CafeteriaERICA.student_erica, "teacher": CafeteriaERICA.teacher_erica,
                           "food_court": CafeteriaERICA.food_court_erica, "changbo": CafeteriaERICA.changbo_erica,
                           "dormitory": CafeteriaERICA.dorm_erica}
    restaurant = restaurant_list[request.restaurant]
    return get_recipe(restaurant)


@hanyang_app_router.post('/food')
async def get_food_menu(request: LanguageRequest):
    return get_recipe_all_cafeteria(request.language)
