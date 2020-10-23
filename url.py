from fastapi import APIRouter
from fastapi.responses import JSONResponse

from transport.shuttle.get_info import get_departure_info
from transport.shuttle.date import is_semester
from transport.bus.get_arrival_info import get_bus_info, get_bus_timetable
from transport.subway.get_info import get_subway_info, get_subway_timetable

from library.reading_room import get_reading_room_seat

from food.menu import CafeteriaSeoul, CafeteriaERICA, get_recipe

from app.common.models import ShuttleRequest, CampusRequest, BusRequest, MenuRequest

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

    if campus:
        return JSONResponse({})
    else:
        return JSONResponse({"realtime": get_bus_info()[request.route],
                             "timetable": [{"time": x["time"].strftime("%H:%M")} for x in
                                           get_bus_timetable(is_weekend)[request.route]]})


@hanyang_app_router.post('/library')
async def get_library_list(request: CampusRequest):
    campus = request.campus == "Seoul"
    response = {}
    for x in get_reading_room_seat(campus=campus)[0]:
        response[x['name']] = {'active': x['activeTotal'], 'occupied': x['occupied'], 'available': x['available']}

    return JSONResponse(response)


@hanyang_app_router.post('/food')
async def get_food_menu(request: MenuRequest):
    campus = request.campus == "Seoul"
    if campus:
        restaurant_list = {"student_1": CafeteriaSeoul.student_seoul_1, "student_2": CafeteriaSeoul.student_seoul_2,
                           "teacher_1": CafeteriaSeoul.teacher_seoul_1, "teacher_2": CafeteriaSeoul.teacher_seoul_2,
                           "dormitory_1": CafeteriaSeoul.dorm_seoul_1, "dormitory_2": CafeteriaSeoul.dorm_seoul_2,
                           "hangwon": CafeteriaSeoul.hangwon_seoul, "sarang": CafeteriaSeoul.sarang_seoul}
    else:
        restaurant_list = {"student": CafeteriaERICA.student_erica, "teacher": CafeteriaERICA.teacher_erica,
                           "foodcoart": CafeteriaERICA.foodcoart_erica, "changbo": CafeteriaERICA.changbo_erica,
                           "dormitory": CafeteriaERICA.dorm_erica}
    restaurant = restaurant_list[request.restaurant]
    return get_recipe(campus=campus, cafeteria=restaurant)
