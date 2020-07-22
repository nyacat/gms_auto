import logging
from aiohttp import web


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status == 404:
            logging.warning("File: {} not found in local folder, redirect to nexon server".format(request.path))
            raise web.HTTPFound("http://download2.nexon.net{}".format(request.path))
        else:
            return response
    except web.HTTPException as ex:
        if ex.status == 404:
            logging.warning("File: {} not found in local folder, redirect to nexon server".format(request.path))
            raise web.HTTPFound("http://download2.nexon.net{}".format(request.path))
        else:
            raise


def start_web(file_path, http_port):
    app = web.Application(middlewares=[error_middleware])
    app.router.add_static('/Game', path=file_path, show_index=True)
    logging.basicConfig(level=logging.INFO)
    web.run_app(app, host="127.0.0.1", port=http_port, access_log_format='%t "%r" %s %b')
