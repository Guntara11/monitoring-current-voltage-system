from waitress import serve
from coba_plotly import app

if __name__ == "__main__":
    serve(app.server, host='127.0.0.1', port=8050)