Feature: Resume a scrape run from checkpoint
  As a researcher running a long scrape
  I want the run to resume from the last checkpoint
  So that an interrupt does not lose progress or create duplicates

  Scenario: Resume from existing checkpoint
    Given an existing checkpoint at start index 20
    When a new run reads the checkpoint
    Then scraping starts from index 20

  Scenario: Do not duplicate urls already seen this run
    Given a run that has already seen a job url
    When the same job url appears again in a later batch
    Then it is skipped and not written twice
