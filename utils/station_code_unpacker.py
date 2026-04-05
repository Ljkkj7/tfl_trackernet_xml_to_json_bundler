import csv

def unpack_station_codes():
    station_code_dict = {}
    with open('stationCodes.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == 'Timetable Code' or row[0] == '':
                continue
            station_code_dict[row[0]] = row[1]
    return station_code_dict