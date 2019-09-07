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


def getTpScore(athlete_data, prescribed_data):
    # Hours
    total_minutes_completed = athlete_data['hours']*60
    total_minutes_prescribed = prescribed_data['minutes_prescribed']

    if total_minutes_prescribed == 0:
        hours_score = 100.0
    else:
        hours_score = min(100*total_minutes_completed/total_minutes_prescribed, 100.0)  # If the score is over 100, give a score of 100

    # Lift/Regan
    lifts_completed = athlete_data['numLifts']
    regan_completed = athlete_data['numRegan']
    lifts_prescribed = prescribed_data['lifts_prescribed']
    regan_prescribed = prescribed_data['regan_prescribed']
    if lifts_prescribed + regan_prescribed == 0:
        lift_and_regan_score = 100
    else:
        lift_and_regan_score = min(100*(lifts_completed+regan_completed)/(lifts_prescribed+regan_prescribed), 100.0)

    # HR Tracking
    completedZones = [athlete_data['hrZone1'], athlete_data['hrZone2'], athlete_data['hrZone3'], athlete_data['hrZone4'], athlete_data['hrZone5']]
    prescribedZones = [prescribed_data['zone_1_time'], prescribed_data['zone_2_time'], prescribed_data['zone_3_time'], prescribed_data['zone_4_time'], prescribed_data['zone_5_time']]
    totalZoneComp = sum(completedZones) 
    totalZonePresc = sum(prescribedZones) 

    if totalZonePresc == 0:
        hr_tracking_score = 100.0
    else:
        hr_tracking_score = min(100*totalZoneComp/totalZonePresc, 100.0)

    # Zone Adherence
    if totalZoneComp == 0:
        completedZonePercents = [0]*5
    else:
        completedZonePercents = [100*currZone/totalZoneComp for currZone in completedZones]
    if totalZonePresc == 0:
        prescribedZonePrecents = [0]*5
    else:
        prescribedZonePrecents = [100*currZone/totalZonePresc for currZone in prescribedZones]
    percentDiffs = list() 
    for i in range(5):
        percentDiffs.append(abs(completedZonePercents[i]-prescribedZonePrecents[i]))
    
    if totalZoneComp == 0:
        zone_adherence_score = 0
    else:
        zone_adherence_score = min(100 - (sum(percentDiffs)/2), 100.0)

    tp_score = (hours_score*.6 + lift_and_regan_score*.2 + hr_tracking_score * .15 + zone_adherence_score * .05)
    return tp_score
