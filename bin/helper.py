import sys
import requests
import json

def splunkd_auth_header(session_key):
    return {'Authorization': 'Splunk ' + session_key}

def get_jira_settings(server_uri, session_key):
    result = dict()
    for k,v in get_jira_action_config(server_uri, session_key).items():
        if k.startswith('jira'):
            result[k] = v
    result['jira_password'] = get_jira_password(server_uri, session_key)
    return result

def validate_jira_settings(jira_settings):
    url = jira_url(jira_settings, '/myself')
    requests.get(
        url=url,
        auth=(jira_settings.get('jira_username'), jira_settings.get('jira_password')),
        verify=False,
        timeout=10
    ).json()
    return True

def update_jira_settings(jira_settings, server_uri, session_key):
    r = requests.post(
        url=server_uri+'/servicesNS/nobody/jira-send-command/configs/inputs/jirasend?output_mode=json',
        data={
            'jira_url': jira_settings.get('jira_url'),
            'jira_username': jira_settings.get('jira_username')
        },
        headers=splunkd_auth_header(session_key),
        verify=False).json()
    requests.post(
        url=server_uri + '/servicesNS/nobody/jira-send-command/storage/passwords/%3Ajirasend_password%3A?output_mode=json',
        data={
            'password': jira_settings.get('jira_password')
        },
        headers=splunkd_auth_header(session_key),
        verify=False)

def get_jira_password(server_uri, session_key):
    password_url = server_uri + '/servicesNS/nobody/jira-send-command/storage/passwords/%3Ajirasend_password%3A?output_mode=json'

    try:
        # attempting to retrieve cleartext password, disabling SSL verification for practical reasons
        result = requests.get(url=password_url, headers=splunkd_auth_header(session_key), verify=False)
        if result.status_code != 200:
            print >> sys.stderr, "ERROR Error: %s" % str(result.json())
    except Exception, e:
        print >> sys.stderr, "ERROR Error sending message: %s" % e
        return False

    splunk_response = json.loads(result.text)
    jira_password = splunk_response.get("entry")[0].get("content").get("clear_password")

    return jira_password

def get_jira_username(server_uri, session_key):
    return get_jira_action_config(server_uri, session_key).get('jira_username')

def get_jira_action_config(server_uri, session_key):
    url = server_uri + '/servicesNS/nobody/jira-send-command/configs/inputs/jirasend?output_mode=json'
    result = requests.get(url=url, headers=splunkd_auth_header(session_key), verify=False)
    return json.loads(result.text)['entry'][0]['content']

def jira_url(jira_settings, endpoint):
    return '%s/rest/api/latest%s' % (jira_settings.get('jira_url'), endpoint)