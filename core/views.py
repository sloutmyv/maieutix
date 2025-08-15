from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Maieutix</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
            }
        </style>
    </head>
    <body>
        <h1>Hello World</h1>
    </body>
    </html>
    """
    return HttpResponse(html)
