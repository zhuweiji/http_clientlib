I'm exploring the potential of client side library where you can import server side code and make HTTP requests with wrapped FastAPI backend endpoints.

The friction I experience when working on HTTP frontend/backends

1. type information and schema is lost across the boundary
   No type inference and validation for payloads and parameters sent from the frontend client to the backend

2. Reliance on out of band information in OpenAPI/Swagger docs
   API schema is not available in the editor

I see the main benefits of this package as:

1. type information is available in the editor
2. endpoint inputs like query params, path params, request body (and cookies and headers etc.) are all immediately apparent to the client-side team
3. endpoint docstrings are available in the editor too
4. this allows frontend backend syncronicity without gRPC-like code gen and heavyweight additional tooling

The caveats are:

1. this works only for python clients and python backends (support for other languages may be possible via FFI?)
2. client must import server code



# This might work for you if:

You're writing a python microservice using Python or a fullstack python application

# Alternatives

tRPC - on JS/TS stacks

Type-safe APIs without code generation
Server and client share TypeScript types
Very popular in Next.js ecosystem
~30k GitHub stars, actively maintained
