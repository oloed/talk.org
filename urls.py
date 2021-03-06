# Copyright 2008 Google Inc.
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


from django.conf.urls.defaults import *

urlpatterns = patterns(
  '',
  (r'^$', 'controllers.posts.index'),
  (r'^posts\.([^/]+)$', 'controllers.posts.raw'),  
  (r'^posts/([^/]+)$', 'controllers.posts.show'),
  (r'^posts/([^/]+)/edit$', 'controllers.posts.edit'),
  (r'^posts/([^/]+)/destroy$', 'controllers.posts.destroy'),
  (r'^create$', 'controllers.posts.create'),
#  (r'^conversation/(.*)$', 'controllers.conversations.show'),
  (r'^archives/(.*)$', 'controllers.neubia.redirect'),
#  (r'^posts/edit/(\d+)$', 'controllers.posts.edit'),
  (r'^profiles$', 'controllers.profiles.index'),
#  (r'^users/create$', 'controllers.users.create'),
  (r'^profiles/edit$', 'controllers.profiles.edit'),
  (r'^profiles/([^/]+)$', 'controllers.profiles.show'),
#  (r'^users/test$', 'controllers.users.test'),
#  (r'^users/view/(\d+)/(\d+)$', 'controllers.users.view'),
)
