import re
from collections import OrderedDict
from sqlalchemy.sql import text as sql_text

# ==== Used for rempte debugging with pycharm
# import pydevd_pycharm
# pydevd_pycharm.settrace('172.17.0.1', port=5678, stdoutToServer=True, stderrToServer=True)
# ==== Used for rempte debugging with pycharm

def enrich_feature(data_service, dataset, feature):
    """
    Enriches the feature based on dataset information. Ex. adding the golfclub_fk
    :param data_service:
    :param dataset:
    :param feature:
    :return:
    """

    if 'golfclub_fk' in data_service.fields:
        feature['properties']['golfclub_fk'] = getGolfclubFk(dataset)

    # switch(getTheme()) {
    # case 'holzhaeusern/holzhaeusern':
    #     return 'b36af778-ea90-11ea-8397-0242ac180002';
    #     break;
    # default:
    #     return '';
    # }


def getGolfclubFk(dataset) -> str:
    """
    :return: The UUID for the golfclub
    """

    # TODO: get it from the database table golf.golfclub_info
    folder, schema, table = re.split('/|\.', dataset)
    switcher = {
        'holzhaeusern': 'b36af778-ea90-11ea-8397-0242ac180002'
    }
    return switcher.get(schema)


def get_hole_info(data_service, dataset, identity, key_field_name,
                  value_field_name):
    """Query the db and return a collection of features where the
    requested value used in the editing form is composed used the
    referenced table 'course_info'
    """

    dataset_features_provider = data_service.dataset_features_provider(
        identity, dataset)

    # Split dataset on '/' and '.'
    # E.g. a dataset can be: 'holzhaeusern/holzhaeusern.hole_info'
    folder, schema, table = re.split('/|\.', dataset)

    sql = sql_text((
        """
        SELECT hole_info_id,
               hole_number,
               course_name from {schema}.hole_info AS hole
        JOIN {schema}.course_info AS course
        ON hole.course_info_fk = course.course_info_id;
        """.format(schema=schema)))

    # connect to database and start transaction (for read-only access)
    conn = dataset_features_provider.db.connect()
    trans = conn.begin()

    # execute query
    features = []
    result = conn.execute(sql)

    for row in result:
        props = OrderedDict()
        props[key_field_name] = row[0]
        props[value_field_name] = row[2] + ' - ' + row[1]

        feature = {
            'type': 'Feature',
            'id': row[0],
            'properties': props,
            'geometry': None,
            'crs': None,
            'bbox': None}

        features.append(feature)

    # roll back transaction and close database connection
    trans.rollback()
    conn.close()

    return {
        'feature_collection': {
            'type': 'FeatureCollection',
            'features': features,
            'crs': None,
            'bbox': None
        }
    }
