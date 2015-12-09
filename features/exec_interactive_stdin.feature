# dockerpty: exec_interactive_stdin.feature.
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


Feature: Executing command in a running docker container
  As a user I want to be able to execute a command in a running docker.


  Scenario: Capturing output
    Given I am using a TTY
    And I run "cat" in a docker container with stdin open
    And I start the container
    When I exec "sh -c 'ls -1 / | tail -n 3'" in a running docker container
    Then I will see the output
      """
      tmp
      usr
      var
      """


  Scenario: Sending input
    Given I am using a TTY
    And I run "cat" in a docker container with stdin open
    And I start the container
    When I exec "/bin/cat" in a running docker container with a PTY
    And I type "Hello World!"
    And I press ENTER
    Then I will see the output
      """
      Hello World!
      Hello World!
      """


  Scenario: Capturing errors
    Given I am using a TTY
    And I run "cat" in a docker container with stdin open
    And I start the container
    When I exec "sh -c 'cat | sh'" in a running docker container with a PTY
    And I type "echo 'Hello World!' 1>&2"
    And I press ENTER
    Then I will see the output
      """
      echo 'Hello World!' 1>&2
      Hello World!
      """


  Scenario: Capturing mixed output and errors
    Given I am using a TTY
    And I run "cat" in a docker container with stdin open
    And I start the container
    When I exec "sh -c 'cat | sh'" in a running docker container with a PTY
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
