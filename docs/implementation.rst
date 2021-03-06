.. _testing_with_django_swagger_tester:

**********************************
Implementing Django Swagger Tester
**********************************

This document contains an in-depth explanation on how the package works, and how to best implement it.

Response Validation
===================

Maintaining consistent and error-free documentation can be hard,
and it typically becomes exponentially harder as your documentation increases.
Response documentation in particular, is a combinatorial nightmare, as every API can have multiple methods,
where each method has multiple possible responses.

We suggest solving this problem by testing your response documentation against your actual API responses.
This way, you *know* that your API responses match your documented responses.

This makes it easy to catch and fix documentation errors proactively instead of reactively.

Drf_yasg
--------

If you use `drf_yasg`_ to render your Swagger documentation, you should use the ``drf_yasg`` response validator::

    from django_swagger_tester.drf_yasg import validate_response


Static Schema
-------------

If you render Swagger docs from a file (json or yaml), you should use the ``static_schema`` response validator::

    from django_swagger_tester.static_schema import validate_response

.. Note::

    When testing a static schema, you need to add a ``PATH`` setting, pointing to the schema file.

    See `Configuration <configuration.html>`__ for more info.




Examples
--------

Pytest Implementation
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    def test_response_documentation(client):
        response = client.get('api/v1/test/')

        assert response.status_code == 200
        assert response.json() == expected_response

        # Test Swagger documentation
        validate_response(response=response, method='GET', route='api/v1/test/', ignore_case=[])

Django Test Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class MyApiTest(APITestCase):

        def setUp(self) -> None:
            user, _ = User.objects.update_or_create(username='test_user')
            self.client.force_authenticate(user=user)
            self.path = '/api/v1/test/'

        def test_get_200(self) -> None:
            """
            Verifies that a 200 is returned for a valid GET request to the /test/ endpoint.
            """
            response = self.client.get(self.path, headers={'Content-Type': 'application/json'})
            expected_response = [...]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

            # Test Swagger documentation
            validate_response(response=response, method='GET', route=self.path)

.. Note::

    It can be useful to test multiple responses at the same time::

        def test_response_documentation(client):
            # 201 - Resource created
            response = client.post(...)
            validate_response(response=response, method='POST', route='api/v1/test/')

            # 200 - if an object exists, return it with a 200 without creating a new resource
            response = client.post(...)
            validate_response(response=response, method='POST', route='api/v1/test/')

            # 400 - Bad data
            response = client.post(...)
            validate_response(response=response, method='POST', route='api/v1/test/')

The ``validate_response`` Function
----------------------------------

The ``validate_response`` function takes three required inputs:

* response
    **description**: The response object returned from an API call.

    **type**: Response

    .. Note::

        Make sure to pass the response object, not the response data.

* method
    **description**: The HTTP method used to get the response.

    **type**: string

    **example**: ``method='GET'``


* route
    **description**: The resolvable path of your API.

    **type**: string

    **example**: ``route='api/v1/test'``


In addition, the function also takes two optional inputs:

* ignore_case
    **description**: List of keys for which we will skip case-validation. This can be useful for when you've made a conscious decision to, e.g., keep an acronym upper-cased although you have camelCase as a general standard.

    **type**: List of strings

    **example**: ``ignore_case=['API', 'IP]``

* verbose
    **description**: Whether to output more detailed error messages.

    **type**: bool

    **default**: ``False``

    **example**: ``verbose=True``


Suggested Use
-------------

The response validation function can be called from anywhere,
but because the tests require a request client it generally makes sense to include
these tests with your existing API view tests.

For example::

    class TestGetCustomers(AuthorizedRequestBase):

        ...

        def test_is_valid(self):
            """
            Verify that we get a 200 from a valid request.
            """
            response = self.get(route='api/v1/customers/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

        def test_swagger_schema(self):
            """
            Verifies that the API response matches the swagger documentation for the endpoint.
            """
            response = self.get(route='api/v1/customers/')
            validate_response(response=response, method='GET', route='api/v1/customers/')

        ...


Input Validation
================

As with your response documentation, it can be useful to test your
request body documentation to ensure it is-, and remains, accurate.

The current input validation function requires that you're using Django Rest Framework's ``Serializer`` for input validation.

Drf_yasg
--------

If you use `drf_yasg`_ to render your Swagger documentation, you should use the ``drf_yasg`` input validator::

    from django_swagger_tester.drf_yasg import validate_input

Static Schema
-------------

If you render Swagger docs from a file (json or yaml), you should use the ``static_schema`` input validator::

    from django_swagger_tester.static_schema import validate_input

.. Note::

    When testing a static schema, you need to add a ``PATH`` setting, pointing to the schema file.

    See `Configuration <configuration.html>`__ for more info.


Example
-------

.. code-block:: python

    from myapp.api.serializers import MySerializer  # your custom serializer
    from django_swagger_tester.drf_yasg import validate_input  # or replace drf_yasg with `static_schema`


    def test_request_body_documentation(client):
        """
        Verifies that our request body documentation is representative of a valid request body.
        """
        validate_input(serializer=MySerializer, method='POST', route='api/v1/test/', camel_case_parser=True)

.. Note::

    The ``camel_case_parser`` argument should be set to ``True`` if your DRF API uses
    `djangorestframework-camel-case <https://github.com/vbabiy/djangorestframework-camel-case>`_'s
    ``CamelCaseJSONParser`` or ``CamelCaseJSONRenderer``.

The ``validate_input`` Function
----------------------------------

The ``validate_input`` function takes three required inputs:

* serializer
    **description**: The Serializer object used for validating API inputs.

    **type**: rest_framework.serializer.Serializer

* method
    **description**: The HTTP method used to get the response.

    **type**: string

    **example**: ``method='GET'``

* route
    **description**: The resolvable path of your API.

    **type**: string

    **example**: ``route='api/v1/test'``


In addition, the function also takes one optional input:

* camel_case_parser
    **description**: Whether or not to convert a camel-cased example to snake case before passing it to your serializer.

    **type**: boolean

    **example**: ``camel_case_parser=True``

.. Note::

    The ``CAMEL_CASE_PARSER`` project setting lets you specify a project-wide default for the ``camel_case_parser`` argument.

    See `configuration <configuration.html#camel-case-parser>`_ for more info.


Suggested Use
-------------

If you have a file for tests related to each view, input validation tests can be added to each file individually, like we would reccomend you do with response validation tests.
However, input validation tests are also well suited to live separately from your API view tests, because they do not require a database or a request client.

This allows you to put all your input tests into one file. This enables you to very simply test a whole suite of endpoints with very little code::

    from django.test import SimpleTestCase
    from django_swagger_tester.drf_yasg import validate_input

    from api.serializers.validation.request_bodies import ValidateDeleteOrderBody, ...


    class TestSwaggerInput(SimpleTestCase):
        endpoints = [
            {
                'api/v1/orders/': [
                    ('POST', ValidateOrderBody),
                    ('PUT', ValidatePutOrderBody),
                    ('DELETE', ValidateDeleteOrderBody)
                ]
            },
            {
                'api/v1/orders/entries/': [
                    ('POST', ValidateEntryBody),
                    ('PUT', ValidatePutEntryBody),
                    ('DELETE', ValidateEntryDeleteBody)
                ]
            },
            {
                'api/v1/orders/directentries/': [
                    ('POST', ValidateDirectEntriesBody),
                    ('PUT', ValidatePutDirectEntriesBody),
                    ('DELETE', ValidateEntryDeleteBody)
                ]
            },
        ]

        def test_swagger_input(self) -> None:
            """
            Verifies that the documented request bodies are valid.
            """
            for endpoint in self.endpoints:
                for route, values in endpoint.items():
                    for method, serializer in values:
                        validate_input(serializer=serializer, method=method, route=route)


Case checking
=============

In addition to providing test functions for input and response validation,
the implements case checking on all documented property names when you run these functions.

``Case`` in this case, refers to which naming convention your project uses for its property names.
For example, it might use
`camelCase <https://en.wikipedia.org/wiki/Camel_case>`_,
`snake_case <https://en.wikipedia.org/wiki/Snake_case>`_,
or other related formats; the point being that once you settle on a convention,
it is important to remain consistent.

Ignoring Keys
-------------

These checks run as background processes in the package, and will raise errors when a suspected
mistake is caught.

If the package finds an inconsistency in your schema that *you would like to keep
as it is*, you can pass a list of the names you would like to ignore using ``ignore_case``.

One example of this could be if you are camel casing your
responses, but you prefer to keep an abbreviation fully capitalized::

    from django_swgger_tester.drf_yasg import validate_response

    ...

    validate_response(..., route='/api/v1/myApi/', ignore_case=['GUID', 'IP'])


Disabling Case Checks
---------------------

If you prefer not to check your Swagger docs' parameter names, you can set ``CASE`` as ``None`` in the Django Swagger Tester settings.

.. _Drf_yasg: https://github.com/axnsan12/drf-yasg
