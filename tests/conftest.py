import os
import subprocess

import pytest


def _git(repo, *args, env=None):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, env=env
    ).stdout.strip()


@pytest.fixture
def make_repo(tmp_path):
    """Build a throwaway repo from (iso_date, subject, body, filename) tuples. Returns (path, shas)."""

    def build(commits):
        repo = tmp_path / "repo"
        repo.mkdir()
        _git(repo, "init", "-q")
        shas = []
        for i, (when, subject, body, filename) in enumerate(commits):
            (repo / filename).write_text(f"change {i}\n" * (i + 1))
            _git(repo, "add", filename)
            env = {
                **os.environ,
                "GIT_AUTHOR_NAME": "Dev",
                "GIT_AUTHOR_EMAIL": "dev@example.com",
                "GIT_COMMITTER_NAME": "Dev",
                "GIT_COMMITTER_EMAIL": "dev@example.com",
                "GIT_AUTHOR_DATE": when,
                "GIT_COMMITTER_DATE": when,
            }
            message = subject + (f"\n\n{body}" if body else "")
            _git(repo, "commit", "-q", "-m", message, env=env)
            shas.append(_git(repo, "rev-parse", "HEAD"))
        return repo, shas

    return build
