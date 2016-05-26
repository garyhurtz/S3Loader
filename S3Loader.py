# -*- coding: UTF-8 -*- #

from jinja2 import BaseLoader, TemplateNotFound
from backends.backends.S3RawBackend import S3RawBackend
from backends.backends.TextCache import TextCache
import os


class S3Loader(BaseLoader):
    """
    S3 template loader

    Template inheritance results in quite a few hits to S3 (i.e. $$).

    Templates are cached on the local filesystem to minimize impact.

    Cache timeout is currently short, but extend it once the templates
    become stable
    """

    def __init__(self, bucket, cachepath, template_folder=u'templates'):
        """

        Loads templates from a S3 bucket, then caches them on the filesystem
        to minimize cost associated with S3 hits.

        To update templates, simply push new templates to S3. The site will
        load the updates upon cache expiration.

        Default cache timeout is 15 mins.

        Path to templates on S3: bucket/template_folder/template_name
        Path to templates on FS: cachepath/template_folder/template_name

        Templates are cached by name, and in text format (vs random name and format, as with
        the werkzeug FileSystemCache). This allows them to be inspected in debug.

        By default, raise TemplateNotFound if the template cannot be found in either
        cache or S3. Override on_template_not_found to change this behavior, such
        as to return an error template.

        :param bucket: the S3 bucket that holds the templates
        :param cachepath: the local directory containing the template cache
        :param template_folder: the template folder (the containing directory)
        """

        # set the backend
        self.backend = S3RawBackend(bucket)

        # set the cache
        self.cache = TextCache(
            path=cachepath,
            timeout=60 * 15  # 15 mins
        )

        self.template_folder = template_folder

    def get_source(self, env, template):

        path = os.path.join(self.template_folder, template)

        # try to retrieve from the cache
        # cache returns None if not found
        result = self.cache.get(path)

        # if the template was found in cache, we know that there
        # have been no changes since Jinja compiled it last time
        # if not, it may have changed so recompile it
        uptodate = bool(result)

        if result is None:

            # the file was not in the cache
            # try the backend
            # backend returns None if not found
            result = self.backend.load(path)

            if result is not None:
                # template found in the backend
                # store the template in cache
                self.cache.set(path, result)

        # if result is still None I didn't find a template
        if result is None:
            result = self.on_template_not_found(path)

        # return the template
        # if we updated the template from the backend, compile it again
        return result.decode(u'utf-8'), None, lambda: uptodate

    def on_template_not_found(self, template):
        """
        Called when the template is not found in cache or backend

        Hook to return a default or error template

        By default raises TemplateNotFound, which eventually raises a 500

        :param template:
        :return:
        """
        raise TemplateNotFound(u'TemplateNotFound: {0}'.format(template))

    def clear(self):
        """
        Clear the cache

        :return:
        """
        self.cache.clear()
