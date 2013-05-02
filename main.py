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
import webapp2
import os
import urllib
import cgi
import time
from datetime import date
from google.appengine.ext.webapp import template
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import db

class DailyBread(db.Model):
    email = db.StringProperty()
    image_key = db.StringProperty()
    image = blobstore.BlobReferenceProperty()
    type = db.StringProperty()

class Comment(db.Model):
    comment = db.StringProperty(multiline=True)
    name = db.StringProperty()
    comment_image = db.StringProperty()
    comment_date = db.StringProperty()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        today = date.today()
        datas = db.GqlQuery("SELECT * FROM DailyBread")
        comments = db.GqlQuery("SELECT * FROM Comment")
        upload_url = blobstore.create_upload_url('/upload')
        template_values = {
            'user': user,
            'today': today,
            'datas': datas,
            'comments': comments,
            'upload_url':upload_url,
            'login': users.create_login_url(self.request.uri),
            'logout': users.create_logout_url(self.request.uri),
        }
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

class UploadBlobHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        blob_image = self.get_uploads('delUpload')[0]
        i = DailyBread(email = str(users.get_current_user()),
                     image_key = str(blob_image.key()),
                     image = blob_image,
                     type = cgi.escape(self.request.get('type')))
        i.put()
        self.redirect('/')

class CommentHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        j = Comment(comment = cgi.escape(self.request.get('comment')),
                       name = cgi.escape(self.request.get('name')),
                       comment_image = cgi.escape(self.request.get('comment_image')),
                       comment_date = str(date.today()))
        j.put()
        self.redirect('/')

class DownloadBlobImage(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

class DelBlobImage(webapp2.RequestHandler):
    def post(self):
        datas = db.GqlQuery("SELECT * FROM DailyBread")
        for d in datas:
            if cgi.escape(d.image_key)==cgi.escape(self.request.get('key')):
                d.delete()
        self.redirect('/')


app = webapp2.WSGIApplication([('/', MainHandler),('/upload', UploadBlobHandler),('/download/([^/]+)?', DownloadBlobImage),('/delapp', DelBlobImage),('/comment', CommentHandler),], debug=True)
