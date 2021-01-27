import re
from collections import OrderedDict
from sqlalchemy.sql import text as sql_text


def get_hole_info(data_service, dataset, identity, key_field_name, value_field_name):

    dataset_features_provider = data_service.dataset_features_provider(
        identity, dataset)

    # Split dataset on '/' and '.'
    # E.g. a dataset can be: 'holzhaeusern/holzhaeusern.hole_info'
    folder, schema, table = re.split('/|\.', dataset)

    sql = sql_text((
        """
        select hole_info_id, hole_number, course_name from {schema}.hole_info as hole
        join {schema}.course_info as course
        on hole.course_info_fk = course.course_info_id;
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
