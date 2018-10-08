Authentication
==============

.. currentmodule:: minecraft.authentication
.. _Yggdrasil: http://wiki.vg/Authentication
.. _LoginResponse: http://wiki.vg/Authentication#Authenticate

The authentication module contains functions and classes to facilitate 
interfacing with Mojang's Yggdrasil_ authentication service.


Logging In
~~~~~~~~~~~~~~~~~~~~

The most common use for this module in the context of a client will be to
log in to a Minecraft account. The first step to doing this is creating
an instance of the AuthenticationToken class after which you may use the
authenticate method with the user's username and password in order to make the AuthenticationToken valid.

.. autoclass:: AuthenticationToken
    :members: authenticate

Upon success, the function returns True, on failure a YggdrasilError
is raised. This happens, for example if an incorrect username/password
is provided or the web request failed.

.. autoexception:: YggdrasilError
    :members:


Arbitrary Requests
~~~~~~~~~~~~~~~~~~~~

You may make any arbitrary request to the Yggdrasil service with the _make_request
method passing in the AUTH_SERVER as the server parameter.

.. automodule:: minecraft.authentication
	:members: AUTH_SERVER

.. autofunction:: _make_request


---------------
 Example Usage
---------------
An example of making an arbitrary request can be seen here::

    payload = {'username': username,
               'password': password}

    authentication._make_request(authentication.AUTH_SERVER, "signout", payload)

