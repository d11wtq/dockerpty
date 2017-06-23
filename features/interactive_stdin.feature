# dockerpty: interactive_stdin.feature.
#
# Copyright 2014 Chris Corbyn <chris@w3style.co.uk>
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


Feature: Attaching to a docker container with stdin open
  As a user I want to be able to attach to a process in a running docker
  and send it data via stdin.


  Scenario: Capturing output
    Given I am using a TTY
    And I run "tail -n1 -f /etc/passwd" in a docker container with stdin open
    When I start dockerpty
    Then I will see output matching
      """
      ^nobody:x:\d+:\d+:nobody:/home:/bin/false$
      """


  Scenario: Sending input
    Given I am using a TTY
    And I run "/bin/cat" in a docker container with stdin open
    When I start dockerpty
    And I type "Hello World!"
    And I press ENTER
    Then I will see the output
      """
      Hello World!
      Hello World!
      """


  Scenario: Capturing errors
    Given I am using a TTY
    And I run "sh -c 'cat | sh'" in a docker container with stdin open
    When I start dockerpty
    And I type "echo 'Hello World!' 1>&2"
    And I press ENTER
    Then I will see the output
      """
      echo 'Hello World!' 1>&2
      Hello World!
      """


  Scenario: Capturing mixed output and errors
    Given I am using a TTY
    And I run "sh -c 'cat | sh'" in a docker container with stdin open
    When I start dockerpty
    And I type "echo 'Hello World!'"
    And I press ENTER
    Then I will see the output
      """
      echo 'Hello World!'
      Hello World!
      """
    When I type "echo 'Hello Universe!' 1>&2"
    And I press ENTER
    Then I will see the output
      """
      echo 'Hello Universe!' 1>&2
      Hello Universe!
      """


  @skip3
  Scenario: Closing input
    Given I am using a TTY
    And I run "/bin/cat" in a docker container with stdin open
    When I start dockerpty
    And I type "Hello World!"
    And I press ENTER
    Then I will see the output
      """
      Hello World!
      Hello World!
      """
    When I press C-d
    Then The PTY will be closed cleanly
    And The container will not be running


  Scenario: Running when the container is started
    Given I am using a TTY
    And I run "/bin/cat" in a docker container with stdin open
    When I start the container
    And I start dockerpty
    And I type "Hello World!"
    And I press ENTER
    Then I will see the output
      """
      Hello World!
      Hello World!
      """
