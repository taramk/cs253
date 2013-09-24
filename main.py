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


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))


class Posts(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Blog(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC ")
        self.render("blog.html", posts=posts)


class NewPost(Handler):
    def render_form(self, subject="", content="", error=""):
        self.render("newpost.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_form()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Posts(subject=subject, content=content)
            p.put()

            self.redirect("post/?created=" + created)
        else:
            error = "We need both a title and content."
            self.render_form(subject, content, error=error)


class Post(Handler):
    def render_post(self, created):
        created = self.request.get('created')
        self.render("post.html", created=created)

    def get(self):
        self.render_post()


class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Ascii(Handler):
    def render_ascii(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC ")
        self.render("ascii.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_ascii()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title=title, art=art)
            a.put()

            self.redirect("ascii")
        else:
            error = "We need both a title and some artwork."
            self.render_ascii(title, art, error=error)


class Rot13(Handler):
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


class Signup(Handler):
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


class Welcome(Handler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username=username)
        else:
            self.redirect('/unit2/signup')


app = webapp2.WSGIApplication([('/unit2/rot13', Rot13),
                               ('/unit2/signup', Signup),
                               ('/unit2/welcome', Welcome),
                               ('/unit3/ascii', Ascii),
                               ('/blog', Blog),
                               ('/blog/newpost', NewPost),
                               ('/blog/post', Post)],
                              debug=True)
