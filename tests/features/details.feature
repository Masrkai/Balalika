Feature: Enrich a job detail page
  As a researcher
  I want each job's detail page fetched for description and salary
  So that listings carry full text and compensation

  Scenario: Extract description and salary from a detail page
    Given the network is available
    And a known LinkedIn job url
    When I fetch the job details
    Then I get a description and an optional salary structure
    And a failure never raises an unhandled exception

  Scenario: Gracefully skip on fetch failure
    Given a job url that cannot be fetched
    When I fetch the job details
    Then the result is a null description and null salary
