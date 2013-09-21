#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
import codecs
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


class Rot13(BaseHandler):
    def get(self):
        self.render('rot13-form.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = codecs.encode(text, 'rot13')

        self.render('rot13-form.html', text=rot13)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
    return email and EMAIL_RE.match(email)


class Signup(BaseHandler):
    def get(self):
        self.render('signup-form.html')

    def post(self):
        errors = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username=username, email=email)

        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            errors = True

        if not valid_password(password):
            params['error_password'] = "That's not a valid password."
            errors = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            errors = True

        if email:
            if not valid_email(email):
                params['error_email'] = "That's not a valid email address."
                errors = True

        if errors:
            self.render('signup-form.html', **params)
        else:
            self.redirect('/unit2/welcome?username=' + username)


class Welcome(BaseHandler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username=username)
        else:
            self.redirect('/unit2/signup')


app = webapp2.WSGIApplication([('/unit2/rot13', Rot13),
                               ('/unit2/signup', Signup),
                               ('/unit2/welcome', Welcome)],
                              debug=True)
