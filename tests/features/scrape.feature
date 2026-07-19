Feature: Parse LinkedIn search results
  As a researcher scraping LinkedIn
  I want search-result HTML turned into structured job records
  So that I can analyze the job market without manual extraction

  Scenario: Extract job fields from a captured search page
    Given a captured LinkedIn search HTML fixture
    When I parse the listings
    Then each job has a title, company, location, and url
    And no salary is the literal string "N/A"

  Scenario: Deduplicate listings by job url
    Given a captured LinkedIn search HTML fixture
    When I parse the listings and collect unique urls
    Then there are no duplicate job urls

  Scenario: Advance the checkpoint when a page is consumed
    Given a parsed batch of 10 jobs starting at index 0
    When the batch is consumed
    Then the next start index is 10
