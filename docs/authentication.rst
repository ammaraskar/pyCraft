Authentication
==============

.. currentmodule:: authentication
.. _Yggdrasil: http://wiki.vg/Authentication
.. _LoginResponse: http://wiki.vg/Authentication#Authenticate

The authentication module contains functions and classes to facilitate 
interfacing with Mojang's Yggdrasil_ service.


Logging In
~~~~~~~~~~~~~~~~~~~~

The most common use for this module in the context of a client will be to
log in to a Minecraft account. The convenience method 

.. autofunction:: login_to_minecraft

should be used which will return a LoginResponse object. See LoginResponse_ for more details on the returned attributes

.. autoclass:: LoginResponse
    :members:

or raise a YggdrasilError on failure, for example if an incorrect username/password
is provided or the web request failed

.. autoexception:: YggdrasilError
    :members:


Arbitary Requests
~~~~~~~~~~~~~~~~~~~~

You may make any arbitary request to the Yggdrasil service with

.. automodule:: authentication
	:members: BASE_URL

.. autofunction:: make_request

.. autoclass:: Response
	:members:


---------------
 Example Usage
---------------
An example of making an arbitary request can be seen here::

	url = "https://sessionserver.mojang.com/session/minecraft/join"
	server_id = encryption.generate_verification_hash(packet.server_id, secret, packet.public_key)

	response = authentication.make_request(url, {'accessToken': self.connection.login_response.access_token,
                                  				'selectedProfile': self.connection.login_response.profile_id,
                                  				'serverId': server_id})

