from django_swagger_tester.drf_yasg.loader import LoadDrfYasgSchema


def mocked_get_path_prefix(*args):
    return '/'


def test_path_prefix(monkeypatch):
    """
    Make sure the get_response_schema function doesn't fail if the path-prefix is '/'.

    Test written to replicate previous bug - don't remove
    """
    route = '/api/v1/cars/correct/'
    monkeypatch.setattr(
        'django_swagger_tester.drf_yasg.loader.LoadDrfYasgSchema.get_path_prefix', mocked_get_path_prefix
    )
    base = LoadDrfYasgSchema(route, 'get', status_code=200)
    base.get_drf_yasg_compatible_route(route)
