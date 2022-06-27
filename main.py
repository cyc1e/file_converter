# from asyncio.subprocess import PIPE, STDOUT
import tempfile

from aiohttp import web
import os
import subprocess


async def converter(request):
    response = web.StreamResponse(
        status=200,
        reason="OK",
    )
    try:
        with tempfile.NamedTemporaryFile() as outputPath:
            formatByUrl = request.rel_url.query.get('format')
            filterByUrl = request.rel_url.query.get('filter')
            if not formatByUrl:
                raise web.HTTPBadRequest(reason='format is required')
            format = formatByUrl
            if filterByUrl != None:
                format = f"'{format}:{filterByUrl}'"
            reader = await request.multipart()
            docx = await reader.next()

            while True:
                chunk = await docx.read_chunk()
                if not chunk:
                    break
                outputPath.write(chunk)
            outputPath.flush()

            command = 'soffice ' \
            '-env:UserInstallation=file:///$HOME/.libreoffice-headless/ ' \
            '--headless ' \
            '--convert-to ' \
            f"'{format}' " \
            '--outdir ' \
            f"'{os.path.abspath(os.path.dirname(outputPath.name))}' " \
            f"'{os.path.abspath(outputPath.name)}' " \
            
            p = subprocess.Popen(command, shell=True, executable='/bin/bash')
            
            p.wait()
            path = f"{outputPath.name}.{formatByUrl}"
            response.content_type = f'application/{formatByUrl}'

            await response.prepare(request)

            with open(path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    await response.write(chunk)
                    await response.drain()
       

            os.remove(path)
            return response
    except Exception as globEx:
        print('globEx', globEx)
        return globEx


if __name__ == '__main__':
    app = web.Application()
    app.router.add_post('/', converter)

    web.run_app(app, port=int(os.getenv('PORT', "6000")))