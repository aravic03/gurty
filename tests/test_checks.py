from datetime import date, datetime, timezone

from sred import checks, draft
from sred.evidence import Evidence, EvidenceIndex

IN_YEAR = "a1b2c3d4e5"
BEFORE_YEAR = "b2c3d4e5f6"
TWIN_1 = "c0ffee0001"
TWIN_2 = "c0ffee0002"


def _ev(sha, day):
    return Evidence(
        sha=sha, parents=["p"], author="Dev", date=datetime.fromisoformat(day).replace(tzinfo=timezone.utc),
        subject="s", body="",
    )


INDEX = EvidenceIndex(
    [
        _ev(IN_YEAR, "2025-05-01"),
        _ev(BEFORE_YEAR, "2024-11-01"),
        _ev(TWIN_1, "2025-05-02"),
        _ev(TWIN_2, "2025-05-03"),
    ]
)
YEAR = {"year_start": date(2025, 1, 1), "year_end": date(2025, 12, 31)}


def _draft(l242="It was unknown whether X could reach Y [a1b2c3d].",
           l244="We tested approach A [a1b2c3d]. It failed at scale [a1b2c3d].",
           l246="We learned Z [a1b2c3d]."):
    return draft.parse(f"# Project: Test\n## Line 242\n{l242}\n## Line 244\n{l244}\n## Line 246\n{l246}\n")


def _checks(report):
    return {(f.check, f.section) for f in report.findings}


def test_clean_draft_passes():
    report = checks.check(_draft(), INDEX, **YEAR)
    assert report.passed, report.findings
    assert report.metrics["citation_resolution_rate"] == 1.0
    assert report.metrics["coverage"]["244"] == 1.0


def test_missing_section_fails():
    parsed = draft.parse("## Line 242\nSomething [a1b2c3d].\n## Line 244\nWork [a1b2c3d].\n")
    report = checks.check(parsed, INDEX)
    assert ("missing-section", "246") in _checks(report)


def test_word_limit_excludes_citations():
    at_limit = " ".join(["word"] * 350) + " [a1b2c3d]."
    assert not ({("word-limit", "242")} & _checks(checks.check(_draft(l242=at_limit), INDEX, **YEAR)))

    over = " ".join(["word"] * 351) + "."
    assert ("word-limit", "242") in _checks(checks.check(_draft(l242=over), INDEX, **YEAR))


def test_unresolved_and_ambiguous_citations_fail():
    report = checks.check(_draft(l246="Made up [deadbee]. Twin [c0ffee0]."), INDEX, **YEAR)
    found = _checks(report)
    assert ("unresolved-citation", "246") in found
    assert ("ambiguous-citation", "246") in found
    assert report.metrics["citation_resolution_rate"] == round(3 / 5, 3)


def test_work_outside_tax_year_fails_only_in_244():
    report = checks.check(
        _draft(l242="Known gap since last year [b2c3d4e].", l244="We did the work [b2c3d4e]."),
        INDEX,
        **YEAR,
    )
    found = _checks(report)
    assert ("outside-tax-year", "244") in found
    assert ("outside-tax-year", "242") not in found


def test_low_coverage_fails():
    report = checks.check(
        _draft(l244="We tried A [a1b2c3d]. We tried B. We tried C. We tried D."), INDEX, **YEAR
    )
    assert report.metrics["coverage"]["244"] == 0.25
    assert ("low-coverage", "244") in _checks(report)


def test_phrase_lints_are_warnings():
    report = checks.check(
        _draft(l242="Integration was challenging and customers wanted a cutting-edge product [a1b2c3d]."),
        INDEX,
        **YEAR,
    )
    lints = {f.check for f in report.findings if f.level == "warning"}
    assert {"difficulty-not-uncertainty", "business-uncertainty", "marketing-language"} <= lints
    assert report.passed


def test_parse_handles_lists_and_multiple_citations():
    parsed = draft.parse(
        "# Project: Cache\n## Line 244\n- Built harness [a1b2c3d, b2c3d4e].\n- Ran it.\n"
    )
    section = parsed.sections["244"]
    assert parsed.title == "Cache"
    assert [s.citations for s in section.sentences] == [["a1b2c3d", "b2c3d4e"], []]
