MIN_PERCENTAGE = .5


def getZonePercents(data):
    hrZone1 = data['hrZone1']
    hrZone2 = data['hrZone2']
    hrZone3 = data['hrZone3']
    hrZone4 = data['hrZone4']
    hrZone5 = data['hrZone5']
    if hrZone1 is None or hrZone2 is None or hrZone3 is None or hrZone4 is None or hrZone5 is None:
        hrZonesSum = None
    else:
        hrZonesSum = hrZone1 + hrZone2 + hrZone3 + hrZone4 + hrZone5

    powerZone1 = data['powerZone1']
    powerZone2 = data['powerZone2']
    powerZone3 = data['powerZone3']
    powerZone4 = data['powerZone4']
    powerZone5 = data['powerZone5']
    if powerZone1 is None or powerZone2 is None or powerZone3 is None or powerZone4 is None or powerZone5 is None:
        powerZonesSum = None
    else:
        powerZonesSum = powerZone1 + powerZone2 + powerZone3 + powerZone4 + powerZone5

    totalMinutes = data['hours'] * 60

    invalid_hr_zones = {
        'hrZone1Percent': '-',
        'hrZone2Percent': '-',
        'hrZone3Percent': '-',
        'hrZone4Percent': '-',
        'hrZone5Percent': '-'
    }

    invalid_power_zones = {
        'powerZone1Percent': '-',
        'powerZone2Percent': '-',
        'powerZone3Percent': '-',
        'powerZone4Percent': '-',
        'powerZone5Percent': '-'
    }

    if totalMinutes == 0 or hrZonesSum is None or powerZonesSum is None:
        return invalid_hr_zones, invalid_power_zones

    if(hrZonesSum/totalMinutes > MIN_PERCENTAGE):
        hr_zones = {
            'hrZone1Percent': round(hrZone1/hrZonesSum * 100, 1),
            'hrZone2Percent': round(hrZone2/hrZonesSum * 100, 1),
            'hrZone3Percent': round(hrZone3/hrZonesSum * 100, 1),
            'hrZone4Percent': round(hrZone4/hrZonesSum * 100, 1),
            'hrZone5Percent': round(hrZone5/hrZonesSum * 100, 1)
        }
    else:
        hr_zones = invalid_hr_zones

    if(powerZonesSum/totalMinutes > MIN_PERCENTAGE):
        power_zones = {
            'powerZone1Percent':round(powerZone1/powerZonesSum * 100, 1),
            'powerZone2Percent':round(powerZone2/powerZonesSum * 100, 1),
            'powerZone3Percent':round(powerZone3/powerZonesSum * 100, 1),
            'powerZone4Percent':round(powerZone4/powerZonesSum * 100, 1),
            'powerZone5Percent':round(powerZone5/powerZonesSum * 100, 1)
        }
    else:
        power_zones = invalid_power_zones

    return hr_zones, power_zones
