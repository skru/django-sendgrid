#!/usr/bin/python
# Version 1.0
# Last Updated 6/22/2009
# From http://docs.sendgrid.com/documentation/api/smtp-api/python-example/
import json
import re
import textwrap


class SmtpApiHeader:
    def __init__(self):
        self.data = {}

    def addTo(self, to):
        if 'to' not in self.data:
            self.data['to'] = []
        if type(to) is str:
            self.data['to'] += [to]
        else:
            self.data['to'] += to

    def addSubVal(self, var, val):
        if 'sub' not in self.data:
            self.data['sub'] = {}
        if type(val) is str:
            self.data['sub'][var] = [val]
        else:
            self.data['sub'][var] = val

    def setUniqueArgs(self, val):
        if type(val) is dict:
            self.data['unique_args'] = val

    def setCategory(self, cat):
        self.data['category'] = cat

    def addFilterSetting(self, fltr, setting, val):
        if 'filters' not in self.data:
            self.data['filters'] = {}
        if fltr not in self.data['filters']:
            self.data['filters'][fltr] = {}
        if 'settings' not in self.data['filters'][fltr]:
                self.data['filters'][fltr]['settings'] = {}
        self.data['filters'][fltr]['settings'][setting] = val

    def asJSON(self):
        j = json.dumps(self.data)
        return re.compile('(["\]}])([,:])(["\[{])').sub('\1\2 \3', j)

    def as_string(self):
        j = self.asJSON()
        str = 'X-SMTPAPI: %s' % textwrap.fill(j, subsequent_indent='    ', width=72)
        return str
