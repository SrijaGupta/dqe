#
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER
#
# Copyright (c) 2015 Juniper Networks, Inc.
# All rights reserved.
#
# Use is subject to license terms.
#
# Licensed under the Apache License, Version 2.0 (the ?License?); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from setuptools import setup, find_packages

setup(name='py-os-vnfstack',
      version='0.0.1',
      author='Subrata Mazumdar',
      author_email='subratam@juniper.net',
      packages=find_packages(),
      # package_data={},
      # package_data={'jnpr.jedi.space.util': ['run_jinja2_render.sh',
      #                              'template_params/*.*'
      #                              ]},
      install_requires=['future>=0.14.3',
                        'requests>=2.5.1',
                        'lxml>=3.3.5',
                        'PyYAML>=3.11',
                        'pytest>=2.5.2',
                        'jinja2>=2.7.3'],
      python_requires='>=2.7',
      classifiers=[
                   'Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Information Technology',
                   'Intended Audience :: System Administrators',
                   'Intended Audience :: Telecommunications Industry',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   # 'Programming Language :: Python :: 3.3',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Software Development :: Libraries :: Application Frameworks',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: System :: Networking',
                   'Topic :: Text Processing :: Markup :: XML'
                   ]
      )
