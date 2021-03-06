from blockchain import Block, Blockchain
import argparse
from flask import Flask, jsonify, request
import requests


app = Flask(__name__)

chain = None


def get_other_nodes():
    http_response = requests.get(
        'http://localhost:5001/list')
    response = http_response.json()
    nodes = response["nodes"]
    return nodes


def connect_to_network(port):
    data = {'port': port}
    http_response = requests.post(
        'http://localhost:5001/connect', json=data)
    if http_response.status_code == 200:
        print('>>> Bilgilendirme: Blockchain ağına bağlanıldı.')
    else:
        print('>>> Hata: {0}'.format(http_response.json()['message']))


def create_chain():
    global chain
    print('>>> Bilgilendirme: Genesis-time:zero')
    chain = Blockchain()


def load_chain(current_port, nodes=None):
    all_blocks = []
    from requests.exceptions import ConnectionError
    for node in nodes:
        try:
            # kendi kendisine chain sormaması için.
            if(node != current_port):
                http_response = requests.get(
                    'http://localhost:{0}/chain'.format(node))
                serialized = http_response.json()['blocks']
                # todo: list of Block deserializer'ının yazılması gerekiyor
                all_blocks.append((node, serialized))
        except ConnectionError as con:
            print(
                '>>> Bilgilendirme: {0} porta sahip node, online görünmüyor'.format(node))

    print('>>> DEV: gelen diğer blocklar' + str(all_blocks))
    if not chain:
        # tüm node'lar kontrol edilmiş fakat yaratılmış bir chain bulunamamışsa, genesis gerçekleşir.
        create_chain()


@app.route('/chain', methods=['GET'])
def get_chain():
    import json
    serialized = json.dumps(
        chain.blocks, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    print('>>>> seri:' + str(serialized))
    return jsonify({'blocks': serialized})


@app.route('/mine', methods=['GET'])
def new_block_added_triggered():
    # yeni eklenen block'un problemini çözmeye çalış
    return jsonify({'status': 'ok'})


@app.route('/add', methods=['POST'])
def add_new_block():
    # tx'i alıp blockchain'e ver. o da block yaratsın.
    return jsonify({'status': 'ok'})


def run(node_port):
    app.run(debug=False, port=node_port)


def get_parser():
    parser = argparse.ArgumentParser(
        description='Blockchain')
    parser.add_argument('-p', '--port',
                        help='node\'un port\'unu belirtir.', type=int)
    parser.add_argument('-m', '--miner',
                        help='node\'un mine işlemi yapıp yapmayacağını belirtir. 0 ya da 1 olmalıdır.', type=int)

    return parser


def command_line_runner():
    parser = get_parser()
    args = parser.parse_args()
    current_port = args.port

    connect_to_network(current_port)

    nodes = get_other_nodes()
    if len(nodes) == 1:
        """
        mevcut node sayısı 1 ise, ilk node network'e bağlanmıştır. 
        bu durumda chain'in ilk kez yaratılması gerekir, doğal olarak da genesis'in.
        """
        create_chain()
    else:
        """
        bu durumda, ağda başka node'lar var demektir. yani bir blockchain ve genesis block'u çoktan yaratılmıştır.
        ağa 1. olarak dahil olmayan tüm node'lar, giriş anlarında mevcut chain'i almaları gerekmektedir.
        """

        load_chain(current_port, nodes=nodes)
    run(current_port)


if __name__ == '__main__':
    command_line_runner()
