import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from pairinglib import PairingStatus, PairResolver

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    d = {
        'EnemyP1': 'EnemyPlayer1', 'EnemyP2': 'EnemyPlayer2', 'EnemyP3': 'EnemyPlayer3',
        'OurP1': 'OurPlayer1', 'OurP2': 'OurPlayer2', 'OurP3': 'OurPlayer3',
    }
    return render_template("index.html", d=d)


@app.route("/", methods=["POST"])
def pair():
    d = request.form.to_dict()
    print(request.form)

    # if step 1: check that everything is filled
    if request.form['action'] == "Calculate step1":
        f = request.form

        valid = check_base_validity(f)
        if not valid:
            d.update({'result': "Some necessary fields are unfilled or player's names are the same"})
            return render_template("index.html", d=d)

        result = step1(f)
        d.update({'result': result})
        return render_template("index.html", d=d)

    # if step 2: check that names match
    if request.form['action'] == "Calculate step2":
        f = request.form

        valid = check_base_validity(f)
        if not valid:
            d.update({'result': "Some necessary fields are unfilled or player's names are the same"})
            return render_template("index.html", d=d)

        valid = check_step2_validity(f)
        if not valid:
            d.update({'result': "Defender's names are not from team's players lists"})
            return render_template("index.html", d=d)

        result = step2(f)
        d.update({'result': result})
        return render_template("index.html", d=d)

    return render_template("index.html", d=d)


def check_base_validity(f: dict) -> bool:
    return (
            f['EnemyP1'] != f['EnemyP2'] != f['EnemyP3'] != '' and
            f['OurP1'] != f['OurP2'] != f['OurP3'] != '' and
            all(f[f'OP{x}_EP{y}'] != '' for x in range(1, 4) for y in range(1, 4))
    )


def check_step2_validity(f: dict) -> bool:
    return (
            f['OD'] in {f['OurP1'], f['OurP2'], f['OurP3']} and
            f['ED'] in {f['EnemyP1'], f['EnemyP2'], f['EnemyP3']}
    )


def init_pair_and_resolver(f) -> (PairingStatus, PairResolver):
    st = PairingStatus(
        opa={f['OurP1'], f['OurP2'], f['OurP3']},
        epa={f['EnemyP1'], f['EnemyP2'], f['EnemyP3']}
    )

    scores = np.array([int(f[f'OP{x}_EP{y}']) for x in range(1, 4) for y in range(1, 4)]).reshape(3, 3)
    scores = pd.DataFrame(
        data=scores,
        index=[f['OurP1'], f['OurP2'], f['OurP3']],
        columns=[f['EnemyP1'], f['EnemyP2'], f['EnemyP3']]
    )
    resolver = PairResolver(scores=scores)
    return st, resolver


def step1(f: dict) -> str:
    st, resolver = init_pair_and_resolver(f)
    st = resolver.resolve_step1(st)
    return str(st).replace('\n', '<br>')


def step2(f: dict) -> str:
    st, resolver = init_pair_and_resolver(f)
    st.our_defender = f['OD']
    st.enemy_defender = f['ED']
    st.opa = st.opa.difference({f['OD']})
    st.epa = st.epa.difference({f['ED']})
    st = resolver.resolve_step2(st)
    return str(st).replace('\n', '<br>')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8088, debug=True)
