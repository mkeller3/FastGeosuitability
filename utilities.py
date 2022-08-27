
def get_final_scores(geojson_collection: object, variables: list) -> object:

    maximum_values = {}

    minimum_values = {}

    for variable in variables:
        column = f"{variable.table}_{variable.type}_{variable.column}"
        for feature in geojson_collection['features']:
            if column not in maximum_values:
                if column in feature['properties']:
                    maximum_values[column] = float(feature['properties'][column])
            else:
                if column in feature['properties']:
                    if float(feature['properties'][column]) > maximum_values[column]:
                        maximum_values[column] = float(feature['properties'][column])
            if column not in minimum_values:
                if column in feature['properties']:
                    minimum_values[column] = float(feature['properties'][column])
            else:
                if column in feature['properties']:
                    if float(feature['properties'][column]) < minimum_values[column]:
                        minimum_values[column] = float(feature['properties'][column])

    for variable in variables:
        column = f"{variable.table}_{variable.type}_{variable.column}"
        for feature in geojson_collection['features']:
            if column in feature['properties']:
                if variable.influence == 'low':
                    if float(feature['properties'][column]) == maximum_values[column]:
                        weighted_score = 0
                        score = 0
                    else:
                        score = (
                            ( maximum_values[column] - float(feature['properties'][column]) ) /
                            ( maximum_values[column] - minimum_values[column] )
                        )
                        weighted_score = score * variable.weight
                    feature['properties'][f"weighted_score_{column}"] = weighted_score
                    feature['properties'][f"score_{column}"] = score
                
                if variable.influence == 'high':
                    if float(feature['properties'][column]) == minimum_values[column]:
                        score = 0
                        weighted_score = 0
                    else:
                        score = (
                            ( float(feature['properties'][column]) - minimum_values[column] ) /
                            ( maximum_values[column] - minimum_values[column] )
                        )
                        weighted_score = score * variable.weight
                    feature['properties'][f"weighted_score_{column}"] = weighted_score
                    feature['properties'][f"score_{column}"] = score
                
                if variable.influence == 'ideal':
                    bottom_score = variable.ideal_value - minimum_values[column]
                    score_max = maximum_values[column] - variable.ideal_value
                    if score_max > bottom_score:
                        bottom_score = score_max
                    score = ( 1 - 
                        (
                            ( abs( variable.ideal_value - float(feature['properties'][column]) ) ) /
                            ( bottom_score )
                        )
                    )
                    weighted_score = score * variable.weight
                    feature['properties'][f"weighted_score_{column}"] = weighted_score
                    feature['properties'][f"score_{column}"] = score
            else:
                feature['properties'][f"weighted_score_{column}"] = 0
                feature['properties'][f"score_{column}"] = score
    
    for feature in geojson_collection['features']:
        final_score = 0
        for variable in variables:
            column = f"{variable.table}_{variable.type}_{variable.column}"
            final_score += feature['properties'][f"weighted_score_{column}"]
        feature['properties']['final_score'] = final_score

    
    geojson_collection['features'] = sorted(geojson_collection['features'] ,key=lambda x: x['properties']['final_score'], reverse=True)

    return geojson_collection