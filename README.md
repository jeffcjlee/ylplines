![Alt text](https://travis-ci.org/jcjl013/ylplines.svg?branch=master "Travis CI Status")
[![Coverage Status](https://coveralls.io/repos/github/jcjl013/ylplines/badge.svg?branch=master)](https://coveralls.io/github/jcjl013/ylplines?branch=master)
[![Stories in Ready](https://badge.waffle.io/jcjl013/ylplines.png?label=ready&title=Ready)](https://waffle.io/jcjl013/ylplines)

ylplines - Clarity for Yelp
===================

An open source project to visualize the timeline of ratings and reviews for Yelp businesses.

Project structure:

<ul>
    <li>ylplines (Top-level directory)
        <ul>
            <li>.openshift (Directives to production)</li>
            <li>doc (Project documentation using Sphinx)</li>
            <li>.travis.yml (Directives to CI build provider)</li>
            <li>setup.py (Prequisites and dependencies for project)</li>
            <li>wsgi (Project source top level)
                <ul>
                    <li>djYlplines (Django level for project)
                        <ul>
                            <li>settings.py (Django settings)</li>
                            <li>urls.py (Project urls)</li>
                            <li>wsgi.py (Web server init)</li>
                        </ul>
                    </li>
                    <li>main (Primary Django app)</li>
                    <li>manage.py (Django manage script)</li>
                </ul>
            </li>
        </ul>
    </li>
</ul>

If you want to work with this project:
1. You must obtain an API key from Yelp so that you can execute queries locally.
Create a 'privatekeys' directory under the 'wsgi' directory. Create a json file 'yelpAPI.json' inside
and include your API information (consumer_key, consumer_secret, token, token_secret).

