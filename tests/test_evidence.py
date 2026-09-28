from sred import evidence


def test_load_parses_multiline_bodies_and_numstat(make_repo):
    repo, shas = make_repo(
        [
            ("2025-02-01T10:00:00+00:00", "Add cache", "", "cache.py"),
            (
                "2025-03-01T10:00:00+00:00",
                "Benchmark two eviction strategies",
                "LRU missed the p99 target.\n\nTrying ARC next.",
                "bench.py",
            ),
        ]
    )
    records = evidence.load(repo)

    assert [r.sha for r in records] == list(reversed(shas))
    newest = records[0]
    assert newest.subject == "Benchmark two eviction strategies"
    assert newest.body == "LRU missed the p99 target.\n\nTrying ARC next."
    assert newest.files == ["bench.py"]
    assert newest.insertions == 2
    assert newest.date.date().isoformat() == "2025-03-01"


def test_load_respects_since_until(make_repo):
    repo, _ = make_repo(
        [
            ("2024-12-15T10:00:00+00:00", "Old", "", "a.py"),
            ("2025-06-01T10:00:00+00:00", "In year", "", "b.py"),
        ]
    )
    records = evidence.load(repo, since="2025-01-01", until="2025-12-31")
    assert [r.subject for r in records] == ["In year"]


def test_signal_stats(make_repo):
    repo, _ = make_repo(
        [
            ("2025-01-01T10:00:00+00:00", "wip", "", "a.py"),
            ("2025-01-02T10:00:00+00:00", "Prototype vector index", "Recall was 0.61.", "b.py"),
            ('2025-01-03T10:00:00+00:00', 'Revert "Prototype vector index"', "", "b.py"),
            ("2025-01-04T10:00:00+00:00", "fix typo", "", "c.py"),
        ]
    )
    stats = evidence.signal_stats(evidence.load(repo))

    assert stats["commits"] == 4
    assert stats["with_body"] == 0.25
    assert stats["reverts"] == 1
    assert stats["experiment_word_share"] == 0.5  # the prototype and its revert
    assert stats["first"] == "2025-01-01"


def test_index_resolves_unique_prefixes(make_repo):
    repo, shas = make_repo([("2025-01-01T10:00:00+00:00", "One", "", "a.py")])
    index = evidence.EvidenceIndex(evidence.load(repo))

    assert [r.sha for r in index.resolve(shas[0][:7].upper())] == [shas[0]]
    assert index.resolve("0000000") == []


def test_signal_stats_excludes_bots():
    from datetime import datetime, timezone

    def ev(author, subject):
        return evidence.Evidence(
            sha="0" * 40, parents=["p"], author=author, date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            subject=subject, body="",
        )

    stats = evidence.signal_stats(
        [ev("dependabot[bot]", "Bump x, compare"), ev("renovate", "Update y"), ev("Dev", "wip")]
    )
    assert stats["commits"] == 1
    assert stats["bot_commits"] == 2
    assert stats["experiment_word_share"] == 0.0
