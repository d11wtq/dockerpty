# dockerpty: interactive_terminal.feature.
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


Feature: Attaching to an interactive terminal in a docker container
  As a user I want to be able to attach to a shell in a running docker
  container and control inside my own terminal.


  Scenario: Starting the PTY
    Given I am using a TTY
    And I run "/bin/sh" in a docker container with a PTY
    When I start dockerpty
    Then I will see the output
      """
      / #
      """


  Scenario: Controlling input
    Given I am using a TTY
    And I run "/bin/sh" in a docker container with a PTY
    When I start dockerpty
    And I type "whoami"
    Then I will see the output
      """
      / # whoami
      """


  Scenario: Controlling standard output
    Given I am using a TTY
    And I run "/bin/sh" in a docker container with a PTY
    When I start dockerpty
    And I type "uname"
    And I press ENTER
    Then I will see the output
      """
      / # uname
      Linux
      / #
      """


  Scenario: Controlling standard error
    Given I am using a TTY
    And I run "/bin/sh" in a docker container with a PTY
    When I start dockerpty
    And I type "ls blah"
    And I press ENTER
    Then I will see the output
      """
      / # ls blah
      ls: blah: No such file or directory
      / #
      """


  Scenario: Initializing the PTY with the correct size
    Given I am using a TTY with dimensions 20 x 70
    And I run "/bin/sh" in a docker container with a PTY
    When I start dockerpty
    And I type "stty size"
    And I press ENTER
    Then I will see the output
      """
      / # stty size
      20 70
      / #
      """


  Scenario: Resizing the PTY
    Given I am using a TTY with dimensions 20 x 70
    And I run "/bin/sh" in a docker container with a PTY
    When I start dockerpty
    And I resize the terminal to 30 x 100
    And I type "stty size"
    And I press ENTER
    Then I will see the output
      """
      / # stty size
      30 100
      / #
      """


  Scenario: Resizing the PTY frenetically
    Given I am using a TTY with dimensions 20 x 70
    And I run "/bin/sh" in a docker container with a PTY
    When I start dockerpty
    And I resize the terminal to 30 x 100
    And I resize the terminal to 30 x 101
    And I resize the terminal to 30 x 98
    And I resize the terminal to 28 x 98
    And I resize the terminal to 28 x 105
    And I type "stty size"
    And I press ENTER
    Then I will see the output
      """
      / # stty size
      28 105
      / #
      """


  Scenario: Terminating the PTY
    Given I am using a TTY
    And I run "/bin/sh" in a docker container with a PTY
    When I start dockerpty
    And I type "exit"
    And I press ENTER
    Then The PTY will be closed cleanly
    And The container will not be running


  Scenario: Detaching from the PTY
    Given I am using a TTY
    And I run "/bin/sh" in a docker container with a PTY
    When I start dockerpty
    And I press ENTER
    And I press C-p
    And I press C-q
    Then The PTY will be closed cleanly
    And The container will still be running


  Scenario: Reattaching to the PTY
    Given I am using a TTY
    And I run "/bin/sh" in a docker container with a PTY
    When I start dockerpty
    And I type "uname"
    And I press ENTER
    And I press C-p
    And I press C-q
    Then The PTY will be closed cleanly
    When I start dockerpty
    And I press ENTER
    And I press UP
    And I press ENTER
    Then I will see the output
      """
      / # uname
      Linux
      / #
      """


  Scenario: Cleanly exiting on race conditions
    Given I am using a TTY
    And I run "/bin/true" in a docker container with a PTY
    When I start dockerpty
    Then The PTY will be closed cleanly


  Scenario: Running when the container is started
    Given I am using a TTY
    And I run "/bin/sh" in a docker container with a PTY
    When I start the container
    And I start dockerpty
    And I press ENTER
    Then I will see the output
      """
      / #
      """
