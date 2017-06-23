# dockerpty: exec_non_interactive.feature.
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


Feature: Executing command in a running docker container non-interactively
  As a user I want to be able to execute a command in a running docker
  container and view its output in my own terminal.


  Scenario: Capturing output
    Given I am using a TTY
    And I run "cat" in a docker container with stdin open
    And I start the container
    When I exec "/bin/tail -f -n1 /etc/passwd" in a running docker container
    Then I will see output matching
      """
      ^nobody:x:\d+:\d+:nobody:/home:/bin/false$
      """


  Scenario: Capturing errors
    Given I am using a TTY
    And I run "cat" in a docker container with stdin open
    And I start the container
    When I exec "sh -c 'tail -f -n1 /etc/passwd 1>&2'" in a running docker container
    Then I will see output matching
      """
      ^nobody:x:\d+:\d+:nobody:/home:/bin/false$
      """


  Scenario: Ignoring input
    Given I am using a TTY
    And I run "cat" in a docker container with stdin open
    And I start the container
    When I exec "/bin/tail -f -n1 /etc/passwd" in a running docker container
    And I press ENTER
    Then I will see output matching
      """
      ^nobody:x:\d+:\d+:nobody:/home:/bin/false$
      """
    And The container will still be running
