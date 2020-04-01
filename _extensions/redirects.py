# Adapted from https://github.com/sphinx-contrib/redirects

import os
import re

from sphinx.builders import html as builders
from sphinx.util import logging as logging

TEMPLATE = '<html><head><meta http-equiv="refresh" content="0; url=%s"/></head></html>'

logger = logging.getLogger(__name__)

def generate_redirects(app):
    path = os.path.join(app.srcdir, app.config.redirects_file)
    if not os.path.exists(path):
        logger.info("Could not find redirects file at '%s'" % path)
        return

    source_suffix = next(iter(app.config.source_suffix))

    if not type(app.builder) == builders.StandaloneHTMLBuilder:
        logger.info("Redirects are only supported by the 'html' builder. Skipping...")
        return

    with open(path) as redirects:
        pattern = re.compile(r"^([\w./ ]+)(#.*)?$")
        for line in redirects.readlines():
            match_result = pattern.search(line)
            if not match_result:
                continue

            redirect = match_result.group(1).rstrip()
            if redirect.count(' ') != 1:
                logger.error("Ignoring malformed redirection: %s" % redirect)
                continue
            from_path, to_path = redirect.split()
            logger.debug("Redirecting '%s' to '%s'" % (from_path, to_path))

            from_path = from_path.replace(source_suffix, '.html')
            to_path_prefix = '..%s' % os.path.sep * (len(from_path.split(os.path.sep)) - 1)
            to_path = to_path_prefix + to_path.replace(source_suffix, '.html')

            redirected_filename = os.path.join(app.builder.outdir, from_path)
            redirected_directory = os.path.dirname(redirected_filename)
            if not os.path.exists(redirected_directory):
                os.makedirs(redirected_directory)

            with open(redirected_filename, 'w') as f:
                f.write(TEMPLATE % to_path)


def setup(app):
    app.add_config_value('redirects_file', 'redirects', 'env')
    app.connect('builder-inited', generate_redirects)
