Feature: Merge device shards
  As a researcher combining device outputs
  I want shards merged into one canonical file
  So that duplicates across devices are removed and data is extensible

  Scenario: Merge dedups by job url
    Given two device shards with one overlapping job url
    When I merge the shards
    Then the canonical output has no duplicate job urls
    And the row count equals the number of unique job urls

  Scenario: Merge is idempotent
    Given a merged canonical output
    When I merge again
    Then the output is unchanged
