
#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by roadhump
# Copyright (c) 2014 roadhump
#
# License: MIT
#

"""This module exports the Ember Template Linter plugin class."""
import json
import logging
import os
import re
from SublimeLinter.lint import NodeLinter 

logger = logging.getLogger('SublimeLinter.plugin.embertemplatelint')

class EmberTemplateLint(NodeLinter):
    """Provides an interface to the ember template linter executable."""
    cmd = 'ember-template-lint ${file}'

    missing_config_regex = re.compile(
        r'^(.*?)\r?\n\w*(Ember template linter couldn\'t find a configuration file.)',
        re.DOTALL
    )
    regex = (
        r'.+?'
        r'(?P<line>\d+):(?P<col>\d+)'
        r'\s+('
        r'(?P<error>error)'
        r'|'
        r'(?P<warning>warining)'
        r')\s+'
        r'(?P<message>.*)'
        r'\s+'
        r'(?P<ruleId>.*)'
    )
    line_col_base = (1, 0)
    defaults = {
        'selector': 'text.html.handlebars'
    }

    def on_stderr(self, stderr):
        # Demote 'annoying' config is missing error to a warning.
        if self.missing_config_regex.match(stderr):
            logger.warning(stderr)
            self.notify_failure()
        elif (
            'DeprecationWarning' in stderr or
            'ExperimentalWarning' in stderr or
            'in the next version' in stderr  # is that a proper deprecation?
        ):
            logger.warning(stderr)
        else:
            logger.error(stderr)
            self.notify_failure()

    def split_match(self, match):
        match, line, col, error, warning, message, near = super().split_match(match)
        ruleId = match.group("ruleId")

        return match, line, col, ruleId if error is not None else error, ruleId if warning is not None else warning, message, None
