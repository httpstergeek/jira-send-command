import sys
import requests
import json
import os
import platform
try:
    from splunk.clilib import cli_common as cli
except Exception, e:
    print >> sys.stderr, "ERROR Loading splunk.clilib: %s" % e

"""
This class was created using the helpers.py file from jira-alerts created by Splunk's gmelnik
"""


class AppConf:
    def __init__(self, server_uri, session_key):
        self.server_uri = server_uri
        self.session_key = session_key
        self.dir = os.path.dirname(os.path.dirname(__file__))
        self.app = self._get_appname()
        self.password_store = self._password_store()

    def get_config(self, conf, local=False):
        """
        Retrieves local or merged dictionary of dicts local app context.
        This function creates parity for use with writeConfFile in splunk.clilib.
        Should use cli.getMergedConf(), but does not support custom conf files.
        :param conf:  Splunk conf file file name
        :param local: local config only
        :return: dictionary of dicts
        """
        conf = "%s.conf" % conf
        defaultconfpath = os.path.join(self.dir, 'default', conf)
        stanza_dict = cli.readConfFile(defaultconfpath) if os.path.exists(defaultconfpath) else {}
        localconfpath = os.path.join(self.dir, 'local', conf)
        if not local:
            if os.path.exists(localconfpath):
                localconf = cli.readConfFile(localconfpath)
                for setting, stanza in localconf.items():
                    if setting in stanza_dict:
                        stanza_dict[setting].update(stanza)
                    else:
                        stanza_dict[setting] = stanza
        else:
            stanza_dict = cli.readConfFile(localconfpath) if os.path.exists(localconfpath) else {}
        return stanza_dict

    def get_password(self):
        """
        Retrives password from store in plain text
        :return:
        """
        url = "%s%s%s%s%s%s" % (self.server_uri, '/servicesNS/nobody/', self.app,
                                '/storage/passwords/%3A', self.password_store, '%3A?output_mode=json')
        splunk_response = self._get_endpoint(url)
        password = splunk_response.get('entry')[0].get('content').get('clear_password')
        return password

    def get_settings(self, conf):
        """
        Retrieves merged custom config file and password
        :param conf:
        :return:
        """
        results = self.get_config(conf, local=True)
        results[self.password_store] = self.get_password()
        return results

    def update_config(self, conf, stanza_dict):
        """
        Writes dictionary of dicts to local app context
        :param conf: Splunk conf file name
        :param stanza_dict: dictionary of dicts
        :return: True
        """
        conf = "%s.conf" % conf
        localconfpath = os.path.join(self.dir, "local", conf)
        cli.writeConfFile(localconfpath, stanza_dict)
        return True

    def update_settings(self, conf, stanza_dict):
        """
        Updates config file and password store.
        :param conf: Splunk conf file name
        :param stanza_dict: dictionary of dicts
        :return:
        """
        url = "%s%s%s%s%s%s" % (self.server_uri, '/servicesNS/nobody/', self.app,
                                '/storage/passwords/%3A', self.password_store, '%3A?output_mode=json')
        try:
            result = requests.post(url=url,
                                   data={'password': stanza_dict[self.password_store]},
                                   headers=self._splunkd_auth_header(),
                                   verify=False)
            stanza_dict.pop(self.password_store)
            if result.status_code != 200:
                print >> sys.stderr, "ERROR Error: %s" % result.json()
        except Exception, e:
            print >> sys.stderr, "ERROR Error sending message: %s" % e
            return False
        return self.update_config(conf, stanza_dict)

    def _get_appname(self):
        """
        Returns current app context
        :return:
        """
        splitby = '/' if not (platform.system() == 'Windows') else '\\'
        app = self.dir.split(splitby)[-1]
        return app

    def _password_store(self):
        """
        returns password store definition from app.conf
        :return:
        """
        url = "%s%s%s%s" % (self.server_uri, '/servicesNS/nobody/', self.app, '/properties/app?output_mode=json')
        splunk_response = self._get_endpoint(url)
        password_store = None
        for entry in splunk_response['entry']:
            if "credential" in entry['name']:
                password_store = entry['name'].replace('credential::', '').strip(':')
                break
        self.password_store = password_store
        return self.password_store

    def _splunkd_auth_header(self):
        """
        Building dict for request headers
        :return:
        """
        return {'Authorization': 'Splunk ' + self.session_key}

    def _get_endpoint(self, url):
        try:
            # attempting to retrieve cleartext password, disabling SSL verification for practical reasons
            result = requests.get(url=url, headers=self._splunkd_auth_header(), verify=False)
            if result.status_code != 200:
                print >> sys.stderr, "ERROR Error: %s" % str(result.json())
        except Exception, e:
            print >> sys.stderr, "ERROR Error sending message: %s" % e
            return False
        return json.loads(result.text)
