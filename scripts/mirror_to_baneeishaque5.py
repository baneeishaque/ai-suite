#!/usr/bin/env python3
# =====================================================================
# One-click mirror of 5 GitHub repos -> baneeishaque5 (not a fork).
#  - Full mirror clone to local disk (mirror-work/), then mirror push.
#  - Git LFS objects (acers-backend db_dumps) fetched + re-uploaded.
#  - refs/pull/* are stripped before pushing (GitHub rejects them).
#  - Credentials come from environment variables; fully non-interactive.
# REQUIRES on the server: git, git-lfs, python3 (stdlib only)
#   Debian/Ubuntu:  apt-get update && apt-get install -y git git-lfs
# SECURITY: no tokens are embedded in this file. Provide them via env:
#   SRC_TOKEN=<PAT that reads the source repos> \
#   TGT_TOKEN=<PAT with write access to the target account> \
#   TGT_OWNER=baneeishaque5 \
#   python3 mirror_to_baneeishaque5.py
#   Rotate both tokens after each run.
# =====================================================================
import os, sys, json, shutil, subprocess, urllib.request, urllib.error

SRC_TOKEN = os.environ.get("SRC_TOKEN", "")
TGT_TOKEN = os.environ.get("TGT_TOKEN", "")
TGT_OWNER = os.environ.get("TGT_OWNER", "baneeishaque5")

# (source owner/repo, target repo name). Sources chosen for known token
# access (the sandbox PAT reads all of them). Targets pre-created on the
# account with a "-copy" suffix.
REPOS = [
    ("baneeishaque/ai-suite", "ai-suite-copy"),
    ("baneeishaque-ompventure/oleovista-acers", "oleovista-acers-copy"),
    ("anushadpk/acers-backend", "acers-backend-copy"),
    ("anushadpk/acers-web", "acers-web-copy"),
    ("baneeishaque-ompventure/acers-e2e-cucumber-selenium-maven",
     "acers-e2e-cucumber-selenium-maven-copy"),
]

WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mirror-work")


def run(cmd, cwd=None, env=None):
    print("  $ " + " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True, env=env)


def set_default_branch(repo, branch):
    req = urllib.request.Request(
        "https://api.github.com/repos/{}/{}".format(TGT_OWNER, repo),
        data=json.dumps({"default_branch": branch}).encode(),
        method="PATCH",
        headers={
            "Authorization": "Bearer " + TGT_TOKEN,
            "Accept": "application/vnd.github+json",
            "User-Agent": "mirror-script",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print("  [default-branch] {} -> {} (HTTP {})".format(repo, branch, resp.status))
    except urllib.error.HTTPError as e:
        print("  [default-branch] WARNING could not set {} on {}: HTTP {}".format(branch, repo, e.code))


def mirror(src, tgt_name):
    name = src.split("/")[1]
    src_url = "https://x-access-token:{}@github.com/{}.git".format(SRC_TOKEN, src)
    tgt_url = "https://x-access-token:{}@github.com/{}/{}.git".format(TGT_TOKEN, TGT_OWNER, tgt_name)
    bare = os.path.join(WORK, name + ".git")
    os.makedirs(WORK, exist_ok=True)
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    print("== {} -> {} ==".format(src, tgt_name))
    if os.path.isdir(bare):
        print("  [reuse] existing mirror found, refreshing refs only")
        run(["git", "-C", bare, "remote", "update", "--prune"], env=env)
    else:
        run(["git", "clone", "--mirror", src_url, bare], env=env)
    head = subprocess.run(
        ["git", "-C", bare, "symbolic-ref", "--short", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()
    print("  [head] default branch: {}".format(head))
    pull_refs = [r for r in subprocess.run(
        ["git", "-C", bare, "for-each-ref", "--format=%(refname)", "refs/pull/"],
        capture_output=True, text=True,
    ).stdout.splitlines() if r.strip()]
    for ref in pull_refs:
        run(["git", "-C", bare, "update-ref", "-d", ref], env=env)
    if pull_refs:
        print("  [pull-refs] stripped {} refs/pull/* (hidden refs rejected by GitHub)".format(len(pull_refs)))
    run(["git", "-C", bare, "push", "--mirror", tgt_url], env=env)
    set_default_branch(tgt_name, head)
    lfs = subprocess.run(
        ["git", "-C", bare, "lfs", "ls-files"], capture_output=True, text=True,
    )
    count = len([l for l in lfs.stdout.splitlines() if l.strip()])
    if count:
        print("  [lfs] {} object(s) - fetching from origin, pushing to target".format(count))
        try:
            run(["git", "-C", bare, "lfs", "fetch", "--all", "origin"], env=env)
            run(["git", "-C", bare, "lfs", "push", "--all", tgt_url], env=env)
        except subprocess.CalledProcessError as e:
            print("  [lfs] WARNING LFS step failed (git-lfs installed?): {}".format(e))
    else:
        print("  [lfs] no LFS objects")


def main():
    if shutil.which("git") is None:
        sys.exit("ERROR: git not found on this server (apt-get install -y git)")
    if not SRC_TOKEN or not TGT_TOKEN:
        sys.exit("ERROR: set SRC_TOKEN and TGT_TOKEN environment variables (see header)")
    results = []
    for src, tgt in REPOS:
        try:
            mirror(src, tgt)
            results.append((src, "OK"))
        except subprocess.CalledProcessError as e:
            print("  !!! {} FAILED: {}".format(src, e))
            results.append((src, "FAILED"))
    print("=" * 60)
    for src, status in results:
        print("  {}  {}".format(status.ljust(6), src))
    if any(s != "OK" for _, s in results):
        sys.exit(1)
    print("All repos mirrored. Work dir: {}".format(WORK))


if __name__ == "__main__":
    main()
