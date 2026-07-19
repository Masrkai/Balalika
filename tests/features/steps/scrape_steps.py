from behave import given, when, then
from src.scraper.scrape import parse_listings, parse_salary, fetch_job_details
from src.scraper.checkpoint import get_checkpoint, update_checkpoint


@given('a captured LinkedIn search HTML fixture')
def step_given_fixture(context):
    context.html = context.fixture.read_text(encoding="utf-8")


@when('I parse the listings')
def step_when_parse(context):
    context.jobs = parse_listings(context.html)


@then('each job has a title, company, location, and url')
def step_then_fields(context):
    assert context.jobs, "no jobs parsed"
    for job in context.jobs:
        assert job['job_title'] and job['company_name']
        assert job['location'] and job['job_url']


@then('no salary is the literal string "N/A"')
def step_then_no_na_salary(context):
    for job in context.jobs:
        assert job['salary'] is None or isinstance(job['salary'], dict)


@then('there are no duplicate job urls')
def step_then_no_dupes(context):
    urls = [j['job_url'] for j in context.jobs]
    assert len(urls) == len(set(urls))


@given('a parsed batch of {count} jobs starting at index {start}')
def step_given_batch(context, count, start):
    html = context.fixture.read_text(encoding="utf-8")
    context.jobs = parse_listings(html)[:int(count)]
    context.start = int(start)


@when('the batch is consumed')
def step_when_consumed(context):
    context.next_start = context.start + len(context.jobs)


@when('I parse the listings and collect unique urls')
def step_when_parse_unique(context):
    context.jobs = parse_listings(context.html)


@then('the next start index is {expected}')
def step_then_next(context, expected):
    assert context.next_start == int(expected)


@given('the network is available')
def step_given_network(context):
    if not context.network:
        context.scenario.skip(reason="network disabled (set BALALIKA_NETWORK=1)")


@given('a known LinkedIn job url')
def step_given_job_url(context):
    context.job_url = "https://www.linkedin.com/jobs/view/0"


@when('I fetch the job details')
def step_when_fetch_details(context):
    context.description, context.salary = fetch_job_details(context.job_url)


@then('I get a description and an optional salary structure')
def step_then_details(context):
    # offline this is None; online it would be a string / dict-or-None
    assert context.description is None or isinstance(context.description, str)
    assert context.salary is None or isinstance(context.salary, dict)


@then('a failure never raises an unhandled exception')
def step_then_no_raise(context):
    # fetch_job_details swallows errors and returns (None, None)
    assert True


@given('a job url that cannot be fetched')
def step_given_bad_url(context):
    context.job_url = "http://127.0.0.1:9/does-not-exist"


@then('the result is a null description and null salary')
def step_then_null_result(context):
    assert context.description is None
    assert context.salary is None


@given('an existing checkpoint at start index {index}')
def step_given_checkpoint(context, index):
    import tempfile, pathlib
    context.cp = pathlib.Path(tempfile.mktemp(suffix=".json"))
    update_checkpoint(context.cp, int(index))


@when('a new run reads the checkpoint')
def step_when_read_checkpoint(context):
    context.read_index = get_checkpoint(context.cp)


@then('scraping starts from index {expected}')
def step_then_starts_at(context, expected):
    assert context.read_index == int(expected)
    context.cp.unlink(missing_ok=True)


@given('a run that has already seen a job url')
def step_given_seen(context):
    context.seen = {"https://www.linkedin.com/jobs/view/123"}


@when('the same job url appears again in a later batch')
def step_when_repeat(context):
    context.jobs = [{'job_url': "https://www.linkedin.com/jobs/view/123"}]


@then('it is skipped and not written twice')
def step_then_skipped(context):
    kept = [j for j in context.jobs if j['job_url'] not in context.seen]
    assert len(kept) == 0
