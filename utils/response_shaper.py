def response_shaper(predictions, statuses):
    '''
    Shapes the response into a JSON format.
    '''
    shaped_response = {
        "station": None,
        "last_updated": None,
        "lines": []
    }

    line_map = [{} for _ in range(len(statuses))]

    shaped_response["station"] = predictions[0]["Station"]["@N"]
    shaped_response["last_updated"] = predictions[0]["Station"]["@CurTime"]

    for i, line in enumerate(statuses):
        if line["Line"]["@Name"] == "Circle":
            line_map[i]["name"] = "Circle, Hammersmith & City Line"
        else:   
            line_map[i]["name"] = line["Line"]["@Name"]
        line_map[i]["status"] = line["Status"]["@Description"]
        line_map[i]["status_details"] = line.get("@StatusDetails") or None
        line_map[i]["platforms"] = []
    
    shaped_response["lines"] = line_map

    for line_index, prediction in enumerate(predictions):
        platforms = prediction["Station"]["P"]
        platform_map = [{} for _ in range(len(platforms))]

        for platform_index, platform in enumerate(platforms):
            trains = platform.get("T", [])

            if not trains:
                continue

            if isinstance(trains, dict):
                trains = [trains]

            train_map = [{} for _ in range(len(trains))]

            for train_index, train in enumerate(trains):
                train_map[train_index]['destination'] = train.get('@Destination')
                train_map[train_index]['current_position'] = train.get('@Location')
                train_map[train_index]['eta_seconds'] = train.get('@SecondsTo')

            platform_map[platform_index]['platform'] = platform['@N']
            platform_map[platform_index]['trains'] = train_map
            
            if line_index < len(shaped_response['lines']):
                shaped_response['lines'][line_index]['platforms'] = platform_map
            else:
                break
    return shaped_response