#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2015 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.



from __future__ import absolute_import, division, print_function, unicode_literals

from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option
import sys
from helper import *


@Configuration(local=True)
class JiraSendCommand(StreamingCommand):
    """ Counts the number of non-overlapping matches to a regular expression in a set of fields.
    ##Syntax
    .. code-block::
        countmatches fieldname=<field> pattern=<regular_expression> <field-list>
    ##Description
    A count of the number of non-overlapping matches to the regular expression specified by `pattern` is computed for
    each record processed. The result is stored in the field specified by `fieldname`. If `fieldname` exists, its value
    is replaced. If `fieldname` does not exist, it is created. Event records are otherwise passed through to the next
    pipeline processor unmodified.
    ##Example
    Count the number of words in the `text` of each tweet in tweets.csv and store the result in `word_count`.
    .. code-block::
        | inputlookup tweets | countmatches fieldname=word_count pattern="\\w+" text
    """
    fields = Option(
        doc='''
        **Syntax:** **fields=***<fieldname>*
        **Description:** Comma seperated list of fields in results''',
        require=False)

    project = Option(
        doc='''
        **Syntax:** **project=***<JIRA Project ID>*
        **Description:** Project ID in Jira''',
        require=True)

    summary = Option(
        doc='''
        **Syntax:** **summary=***<string>*
        **Description:** Text for Summary field''',
        require=False)

    description = Option(
        doc='''
        **Syntax:** **description=***<string>*
        **Description:** Text for Description field''',
        require=False)

    issue_type = Option(
        doc='''
        **Syntax:** **pattern=***<Issue Type>*
        **Description:** Jira Issue Type''',
        require=False)

    def stream(self, records):
        self.logger.debug('CountMatchesCommand: %s', self)  # logs command line
        searchinfo = self.metadata.searchinfo
        #app_conf = AppConf(searchinfo.splunkd_uri, searchinfo.session_key)
        # password = app_conf.get_password()
        #config = app_conf.get_config('jirasend')
        #issue_type = self.issue_type if self.issue_type else "Task"
        ISSUE_REST_PATH = "/rest/api/latest/issue"
        # create outbound JSON message body
        if self.fields:
            fields = self.fields.split(',')

        for record in records:
            body = {
                "fields": {
                    "project": {
                        "key": self.project
                    },
                    "summary": self.summary,
                    "description": self.description,
                    "issuetype": {
                        "name": self.issue_type
                    }
                }
            }
            if self.fields:
                for field in fields:
                    if field in record:
                        body['fields'][field] = record[field]

            body = json.dumps(body)
            try:
                headers = {"Content-Type": "application/json"}
                #result = requests.post(url=config['jirasend']['jira_url']+ISSUE_REST_PATH, data=body,
                 #                      headers=headers, auth=(config['jirasend']['jira_username'], config['jirasend']['password']))
            except Exception as e:
                result = "Error: %s" % e
                self.logger.error('Error: %s', self, e)
            #record['status_code'] = "%s" % result.status_code
            #record['response'] = "%s" % result.text
            record['meta'] = "%s" % self.metadata.searchinfo
            yield record


dispatch(JiraSendCommand, sys.argv, sys.stdin, sys.stdout, __name__)