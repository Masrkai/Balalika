Feature: Partition work across devices
  As a researcher scraping at scale
  I want the (country, category, keyword) matrix split across devices
  So that each device owns a disjoint slice with no overlap

  Scenario: Mod-split produces disjoint, complete partitions
    Given the full unit matrix for Germany and Canada
    When I split it across 4 devices by mod
    Then every unit belongs to exactly one device
    And the union of all devices equals the full matrix

  Scenario: Explicit filter selects a subset
    Given the full unit matrix for Germany and Canada
    When I filter to country Germany and category Software Engineering
    Then all selected units are in Germany and Software Engineering
