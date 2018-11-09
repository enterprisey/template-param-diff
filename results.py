#!/usr/bin/env python

import cgitb; cgitb.enable()

import cgi
import datetime
import json
import os
from string import Template
import sys
import urllib

import MySQLdb
from wikitools import wiki
from wikitools import api

TOOL_DIR = "/data/project/apersonbot/public_html/template-param-diff/"

def main():
    page_template = None
    try:
        with open(os.path.join(TOOL_DIR, "template.txt")) as template_file:
            page_template = Template(template_file.read())
    except IOError as error:
        print("<h1>Search Error!</h1><p>I couldn't read the web template.<br /><small>Details: " + str(error) + "</small>")
        sys.exit(0)

    def error_and_exit(error):
        print(page_template.substitute(content="<p class='error'>{}</p>".format(error)))
        sys.exit(0)

    form = cgi.FieldStorage()
    try:
        parsed_templates = form["templates"].value
    except:
        error_and_exit("No templates specified.")

    parsed_templates = parsed_templates.split("\n")
    parsed_templates = filter(len, parsed_templates)
    if len(parsed_templates) < 2:
        error_and_exit("You must specify 2 or more templates.")

    # Query db
    db = MySQLdb.connect(db='enwiki_p', host="enwiki.labsdb", read_default_file=os.path.expanduser("~/replica.my.cnf"))
    cursor = db.cursor()

    with open(os.path.join(TOOL_DIR, "query.txt")) as query_file:
        query_template = Template(query_file.read())

    titles = ",".join("\"{}\"".format(t) for t in parsed_templates)

    cursor.execute(query_template.substitute(titles=titles))
    results = cursor.fetchall()
    content = "<pre>"+str(results)+"</pre>"

    # Display results
    #content = "<table>"
    #content += "<tr><th>Name</th><th>Edit count</th><th>Registration</th><th>Last edit</th></tr>"
    #for result in results:
    #    content += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(wikilink("User:" + result[0]),
    #        edit_counter_link(result[0], "{:,d}".format(int(result[1]))),
    #        display_timestamp(result[2]),
    #        wikilink("Special:Contributions/" + result[0], display_timestamp(result[3])))
    #content += "</table>"

    print(page_template.substitute(content=content))

def wikilink(page_name, link_title=None):
    if not link_title:
        link_title = page_name
    return "<a href='https://en.wikipedia.org/wiki/{0}' title='{0} on English Wikipedia'>{1}</a>".format(page_name, link_title)

main()
