# S3Loader

Flask/Jinja2 template loader.

Loads templates from a S3 bucket, then caches them on the filesystem
to minimize delay/cost associated with S3 hits.

The S3Loader uses the [S3RawBackend](https://github.com/garyhurtz/backends/blob/master/backends/S3RawBackend.py) and the [TextCache](https://github.com/garyhurtz/backends/blob/master/backends/TextCache.py) of the [backends](https://github.com/garyhurtz/backends) project to do the heavy lifting of the S3 and filesystem interfaces.

To update template(s) on a live site, simply push new templates to S3 then the site will
load the updates upon cache expiration (default 15 mins).

## Usage

If you arent familiar with Jinja loaders, take a quick look [here](http://jinja.pocoo.org/docs/dev/api/#loaders).

The S3Loader has the following constructor:

    def __init__(self, bucket, cachepath, template_folder=u'templates'):
        ...

where:

* *bucket* - the name of the S3 bucket you are storing templates in
* *cachepath* - the name of the directory you are using as a cache
* *template_folder* - the folder that holds your templates, which should generally be the same as the *template_folder* parameter you used when you set up your Flask application.

This configures the S3Loader to get templates from the *template_folder* directory, which exists within the *cachepath* folder on the local file system, or within *bucket* on S3.

Or, to put it another way:

<table>
<tr>
<td>Path to templates on S3:</td>
<td>bucket/template_folder/template_name</td>
</tr>
<tr>
<td>Path to templates on the local file system:</td> 
<td>cachepath/template_folder/template_name</td>
</tr>
</table>

If you are using Flask, you can set the loader by assigning it to the application's *jinja_loader* attribute, like this:

    app.jinja_loader = S3Loader(
        bucket=u'your-bucket',
        cachepath=u'template_cache',
        template_folder=u'templates'
    )

In the Flask case, you are most likely converting from a FileSystemLoader (the Flask default) to the S3Loader, so you most likely have a *templates* folder (or whatever you set *template_folder* to when you set up your Flask application) on the root level of your project. Basically all you have to do is upload the templates to S3, apply the S3 loader, then load your page. You should see template_cache appear in your project, and any templates you loaded copied into it.

If you are using Jinja2 directly, then you can do something like this:

    Environment(loader=S3Loader(
        bucket=u'your-bucket', 
        cachepath=u'template_cache', 
        template_folder=u'templates'
    )
    
Templates are cached by name, in text format which allows them to be easily inspected in debug.

By default, the S3Loader raises TemplateNotFound if the template cannot be found in either
the cache or S3. Override on_template_not_found to change this behavior, for example it may make sense to return an error template.
