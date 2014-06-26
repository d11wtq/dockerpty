# dockerpty.
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

Feature: Using a pseudo-terminal

  Scenario: Starting the pseudo-terminal
    Given I am using a terminal with dimensions 20 x 70
    And There is a docker container running
    When I start dockerpty
    Then The pseudo-terminal will have dimensions 20 x 70
    And My terminal will be in raw mode


  Scenario: Controlling terminal input
    Given I am using a terminal with dimensions 20 x 70
    And There is a docker container running
    When I start dockerpty
    And I send the input "finger bob"
    Then The pseudo-terminal will receive input "finger bob"


  Scenario: Controlling terminal output
    Given I am using a terminal with dimensions 20 x 70
    And There is a docker container running
    When I start dockerpty
    And The pseudo-terminal sends the output "MOTD"
    And The pseudo-terminal sends the error "Disk full"
    Then I will receive the output "MOTD"
    And I will receive the error "Disk full"


  Scenario: Resizing the pseudo-terminal
    Given I am using a terminal with dimensions 20 x 70
    And There is a docker container running
    When I start dockerpty
    And I resize my terminal to 30 x 100
    Then The pseudo-terminal will have dimensions 30 x 100


  Scenario: Closing the pseudo-terminal
    Given I am using a terminal with dimensions 20 x 70
    And There is a docker container running
    When I start dockerpty
    And I close the pseudo-terminal's input stream
    Then My terminal will not be in raw mode
