Examples
========

After checking out the code using git you can run:

.. code-block:: console

   pip install . dnslib jinja2 starlette wsproto


Simple Customized QUIC Client
.............

I (Jonas Krause) have developed quic_client.py, a custom QUIC client. This client establishes a QUIC connection to a server and sends data over streams.

To run the quic_client.py, execute:

.. code-block:: console

  python quic_client.py

The quic_client.py includes the following customizations:

- Custom QUIC Client Class: Extends QuicConnectionProtocol to handle specific QUIC events.
- Stream ID Assignment: Sets new stream IDs to 2024 and 2026.
- Data Sending on Streams: Sends the payloads "NPA" and "QUIC" on the two different streams.
- Connection Closing: Automatically closes the connection after sending data.

QUIC Configuration:

- Sets HTTP/3 as the protocol for the QUIC connection.
- Configures idle timeout to 5 seconds.
- Sets the maximum stream data to 2024 bytes.
- Disables certificate verification for development purposes.
- QLOG Logging: Logs the connection details in QLOG format in the /logs directory.

To visualize the QUIC protocol's flow using the QLOG files, simply upload the QLOG files to https://qvis.quictools.info/#/files. This tool allows you to view detailed sequence diagrams and other visual representations, showing the specific flow and behavior of the QUIC protocol in your session.



HTTP/3
------

HTTP/3 server
.............

You can run the example server, which handles both HTTP/0.9 and HTTP/3:

.. code-block:: console

   python examples/http3_server.py --certificate tests/ssl_cert.pem --private-key tests/ssl_key.pem

HTTP/3 client
.............

You can run the example client to perform an HTTP/3 request:

.. code-block:: console

  python examples/http3_client.py --ca-certs tests/pycacert.pem https://localhost:4433/

Alternatively you can perform an HTTP/0.9 request:

.. code-block:: console

  python examples/http3_client.py --ca-certs tests/pycacert.pem --legacy-http https://localhost:4433/

You can also open a WebSocket over HTTP/3:

.. code-block:: console

  python examples/http3_client.py --ca-certs tests/pycacert.pem wss://localhost:4433/ws

Chromium and Chrome usage
.........................

Some flags are needed to allow Chrome to communicate with the demo server. Most are not necessary in a more production-oriented deployment with HTTP/2 fallback and a valid certificate, as demonstrated on https://quic.aiortc.org/

- The `--ignore-certificate-errors-spki-list`_ instructs Chrome to accept the demo TLS certificate, even though it is not signed by a known certificate authority. If you use your own valid certificate, you do not need this flag.
- The `--origin-to-force-quic-on` forces Chrome to communicate using HTTP/3. This is needed because the demo server *only* provides an HTTP/3 server. Usually Chrome will connect to an HTTP/2 or HTTP/1.1 server and "discover" the server supports HTTP/3 through an Alt-Svc header.
- The `--enable-experimental-web-platform-features`_ enables WebTransport, because the specifications and implementation are not yet finalised. For HTTP/3 itself, you do not need this flag.

To access the demo server running on the local machine, launch Chromium or Chrome as follows:

.. code:: bash

  google-chrome \
    --enable-experimental-web-platform-features \
    --ignore-certificate-errors-spki-list=BSQJ0jkQ7wwhR7KvPZ+DSNk2XTZ/MS6xCbo9qu++VdQ= \
    --origin-to-force-quic-on=localhost:4433 \
    https://localhost:4433/

The fingerprint passed to the `--ignore-certificate-errors-spki-list`_ option is obtained by running:

.. code:: bash

  openssl x509 -in tests/ssl_cert.pem -pubkey -noout | \
    openssl pkey -pubin -outform der | \
    openssl dgst -sha256 -binary | \
    openssl enc -base64

WebTransport
............

The demo server runs a :code:`WebTransport` echo service at `/wt`. You can connect by opening Developer Tools and running the following:

.. code:: javascript

  let transport = new WebTransport('https://localhost:4433/wt');
  await transport.ready;

  let stream = await transport.createBidirectionalStream();
  let reader = stream.readable.getReader();
  let writer = stream.writable.getWriter();

  await writer.write(new Uint8Array([65, 66, 67]));
  let received = await reader.read();
  await transport.close();

  console.log('received', received);

If all is well you should see:

.. image:: https://user-images.githubusercontent.com/1567624/126713050-e3c0664c-b0b9-4ac8-a393-9b647c9cab6b.png


DNS over QUIC
-------------

By default the server will use the `Google Public DNS`_ service, you can
override this with the ``--resolver`` argument.

By default the server will listen for requests on port 853, which requires
a privileged user. You can override this with the `--port` argument.

You can run the server locally using:

.. code-block:: console

    python examples/doq_server.py --certificate tests/ssl_cert.pem --private-key tests/ssl_key.pem --port 8053

You can then run the client with a specific query:

.. code-block:: console

    python examples/doq_client.py --ca-certs tests/pycacert.pem --query-type A --query-name quic.aiortc.org --port 8053

Please note that for real-world usage you will need to obtain a valid TLS certificate.

.. _Google Public DNS: https://developers.google.com/speed/public-dns
.. _--enable-experimental-web-platform-features: https://peter.sh/experiments/chromium-command-line-switches/#enable-experimental-web-platform-features
.. _--ignore-certificate-errors-spki-list: https://peter.sh/experiments/chromium-command-line-switches/#ignore-certificate-errors-spki-list
