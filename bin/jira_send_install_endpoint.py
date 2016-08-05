import splunk
import splunk.admin as admin
from helper import *

PASSWORD_PLACEHOLDER = '*******'

class InstallHandler(admin.MConfigHandler):
    def __init__(self, *args):
        admin.MConfigHandler.__init__(self, *args)
        self.shouldAutoList = False

    def setup(self):
        self.supportedArgs.addOptArg('*')

    def handleList(self, confInfo):
        app_conf = AppConf(splunk.getLocalServerInfo(), self.getSessionKey())
        config = app_conf.get_config(self.callerArgs.id)
        settings = config['jirasend'] if 'jirasend' in config else {}
        item = confInfo['jirasend']
        item['jira_url'] = settings['jira_url'] if settings['jira_url'] else 'http://your.server/'
        item['jira_username'] = settings['jira_username'] if settings['jira_username'] else ''
        item['jira_password'] = PASSWORD_PLACEHOLDER

    def handleEdit(self, confInfo):
        if self.callerArgs.id == 'jirasend':
            app_conf = AppConf(splunk.getLocalServerInfo(), self.getSessionKey())
            settings = app_conf.get_settings(self.callerArgs.id)
            settings[self.callerArgs.id] = {}
            if 'jira_url' in self.callerArgs:
                settings[self.callerArgs.id]['jira_url'] = self.callerArgs['jira_url'][0]
            if 'jira_username' in self.callerArgs:
                settings[self.callerArgs.id]['jira_username'] = self.callerArgs['jira_username'][0]
            if 'jira_password' in self.callerArgs:
                password = self.callerArgs['jira_password'][0]
                if password and password != PASSWORD_PLACEHOLDER:
                    settings[app_conf.password_store] = password
            app_conf.update_settings(self.callerArgs.id, settings)

admin.init(InstallHandler, admin.CONTEXT_APP_ONLY)
