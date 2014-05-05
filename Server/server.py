#!/usr/bin/env python
import os,logging,json,jinja2

jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
