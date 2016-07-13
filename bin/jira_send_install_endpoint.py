import splunk
import splunk.admin as admin
from helper import *

PASSWORD_PLACEHOLDER = '*******'

class JiraAlertsInstallHandler(admin.MConfigHandler):
    def __init__(self, *args):
        admin.MConfigHandler.__init__(self, *args)
        self.shouldAutoList = False

    def setup(self):
        self.supportedArgs.addOptArg('*')

    def handleList(self, confInfo):
        jira_settings = get_jira_settings(splunk.getLocalServerInfo(), self.getSessionKey())
        item = confInfo['jirasend']
        item['jira_url'] = jira_settings.get('jira_url', 'http://your.server/')
        item['jira_username'] = jira_settings.get('jira_username')
        item['jira_password'] = PASSWORD_PLACEHOLDER

    def handleEdit(self, confInfo):
        if self.callerArgs.id == 'jirasend':
            jira_settings = get_jira_settings(splunk.getLocalServerInfo(), self.getSessionKey())
            if 'jira_url' in self.callerArgs:
                jira_settings['jira_url'] = self.callerArgs['jira_url'][0]
            if 'jira_username' in self.callerArgs:
                jira_settings['jira_username'] = self.callerArgs['jira_username'][0]
            if 'jira_password' in self.callerArgs:
                password = self.callerArgs['jira_password'][0]
                if password and password != PASSWORD_PLACEHOLDER:
                    jira_settings['jira_password'] = password
            if not validate_jira_settings(jira_settings):
                raise admin.ArgValidationException, "Error connecting to JIRA server"
            update_jira_settings(jira_settings, splunk.getLocalServerInfo(), self.getSessionKey())

admin.init(JiraAlertsInstallHandler, admin.CONTEXT_APP_ONLY)
