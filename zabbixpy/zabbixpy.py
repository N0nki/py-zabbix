import json
import os
import sys
import requests


class ZabbixAPIException(Exception):
    pass


class PyZabbix:

    request_header = {"Content-Type": "application/json-rpc"}
    end_point = "zabbix/api_jsonrpc.php"

    def __init__(self, host: str, user: str, password: str):
        self.url = host + PyZabbix.end_point
        self.user = user
        self.password = password
        self.request_id = 1
        self.auth = None

        login_response = self.do_request('GET', 'user.login', {'user': self.user, 'password': self.password})
        self.auth = login_response['result']

    def do_request(self, method: str, api_method: str, params=None) -> dict:
        """
        Zabbixサーバにリクエストを飛ばす

        arguments:
        * method(str)
        * api_method(str)
        * params(dict optional, default None)

        returns:
        * response_json(dict)
        """
        request_body = {
            'jsonrpc': '2.0',
            'auth': self.auth or None,
            'method': api_method,
            'params': params or {},
            'id': self.request_id
        }
        response = requests.request(method, self.url, headers=PyZabbix.request_header, data=json.dumps(request_body))
        try:
            response_json = self.__get_response_json(response)
            self.request_id += 1
            return response_json
        except ZabbixAPIException as e:
            print(e)

    def __get_response_json(self, response: requests.models.Response) -> dict:
        """
        responseオブジェクトからJSONを取り出しして返す

        arguments:
        * response(response)

        returns:
        * response_json(dict)
        """
        response_json = response.json()
        if "error" not in response_json:
            return response_json
        else:
            error_msg = f"{response_json['error']['code']} {response_json['error']['message']} {response_json['error']['data']}"
            raise ZabbixAPIException(error_msg)

    def logout(self):
        """
        user.logoutのリクエストを飛ばしてトークンを無効化する
        """
        self.do_request('GET', 'user.logout')
