from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from auto_label import create_app, db, cli
from auto_label.models import Abstract, Psentence, Nsentence, Pclause

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Abstract': Abstract, 'Psentence': Psentence, 'Nsentence': Nsentence,
            'Pclause': Pclause}
