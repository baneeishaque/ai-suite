import argparse
import json
import re
import hashlib
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CACHE_FILE = BASE / "opencode" / "cache" / "models.json"
EXTENSIONS_FILE = BASE / "scripts" / "provider-extensions.json"
CONFIG_FILE = BASE / "opencode" / "config" / "opencode.json"
AUTH_FILE = BASE / "opencode" / "share" / "auth.json"
ACCOUNT_FILE = BASE / "opencode" / "share" / "account.json"

def to_env_suffix(suffix):
    return suffix.replace("-", "_").replace(".", "_").upper()

def to_name_suffix(suffix):
    return suffix.replace("-", " ").replace(".", " ").title()

def parse_keywords(path):
    mapping = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = re.match(r'\"([^\"]+)\"\s+(\S+)', line)
            if m:
                mapping[m.group(1)] = m.group(2)
            else:
                parts = line.split(None, 1)
                if len(parts) == 2:
                    mapping[parts[0]] = parts[1]
    return mapping

def parse_extensions(data):
    active = {}
    key_map = {}
    disabled = set()
    for base_id, val in data.items():
        if base_id == "ssot":
            continue
        if isinstance(val, list):
            suffixes = []
            for item in val:
                if isinstance(item, dict):
                    suffixes.append(item["suffix"])
                    key_map[f"{base_id}-{item['suffix']}"] = item.get("key")
                else:
                    suffixes.append(item)
            active[base_id] = suffixes
        elif isinstance(val, dict):
            active_list = []
            for item in val.get("active", []):
                if isinstance(item, dict):
                    active_list.append(item["suffix"])
                    key_map[f"{base_id}-{item['suffix']}"] = item.get("key")
                else:
                    active_list.append(item)
            active[base_id] = active_list
            for s in val.get("disabled", []):
                if isinstance(s, dict):
                    disabled.add(f"{base_id}-{s['suffix']}")
                else:
                    disabled.add(f"{base_id}-{s}")
    return active, disabled, key_map

def build_providers(ssot, extensions_data):
    providers = {}
    for base_id, suffixes in extensions_data.items():
        base = ssot.get(base_id)
        if not base:
            print(f"  [skip] base provider '{base_id}' not found in SSOT")
            continue
        for suffix in suffixes:
            ext_id = f"{base_id}-{suffix}"
            providers[ext_id] = {
                "id": ext_id,
                "env": [f"{e.replace('_API_KEY', '')}_{to_env_suffix(suffix)}_API_KEY" for e in base["env"]],
                "name": f'{base["name"]} ({to_name_suffix(suffix)})',
            }
            for inherited_key in ("npm", "api", "doc", "models"):
                if base.get(inherited_key) is not None:
                    providers[ext_id][inherited_key] = base[inherited_key]
    return providers

def generate_account_id(service_id):
    h = hashlib.sha256(service_id.encode()).hexdigest()[:26]
    return h

def sync_auth(target, active_extensions, key_map, keywords, dry_run):
    active_ids = set()
    changes = {}
    for base_id, suffixes in active_extensions.items():
        for suffix in suffixes:
            ext_id = f"{base_id}-{suffix}"
            active_ids.add(ext_id)
            key_ref = key_map.get(ext_id)
            actual_key = keywords.get(key_ref) if key_ref else None
            if not actual_key:
                print(f"  [warn] no key found for '{ext_id}' (ref: {key_ref})")
                continue
            entry = {"type": "api", "key": actual_key}
            existing = target.get(ext_id, {})
            if existing != entry:
                changes[ext_id] = entry

    disabled_prefixes = set()
    for base_id in active_extensions:
        disabled_prefixes.add(f"{base_id}-")

    in_target = {k for k in target
                 if any(k.startswith(p) for p in disabled_prefixes)}
    stale = in_target - active_ids

    if dry_run:
        for sid in sorted(changes):
            print(f"  auth +{sid}: {changes[sid]}")
        for sid in sorted(stale):
            print(f"  auth -{sid}")
        return bool(changes or stale)

    for sid in stale:
        target.pop(sid, None)
    target.update(changes)
    return bool(changes or stale)

def sync_accounts(target, active_extensions, key_map, keywords, dry_run):
    accounts = target.get("accounts", {})
    active = target.get("active", {})
    account_changes = {}
    active_changes = {}
    stale_accounts = set()

    for base_id, suffixes in active_extensions.items():
        for suffix in suffixes:
            ext_id = f"{base_id}-{suffix}"
            key_ref = key_map.get(ext_id)
            actual_key = keywords.get(key_ref) if key_ref else None
            if not actual_key:
                continue

            existing_id = None
            for aid, acct in accounts.items():
                if acct.get("serviceID") == ext_id:
                    existing_id = aid
                    break

            if existing_id:
                acct_id = existing_id
            else:
                acct_id = generate_account_id(ext_id)

            new_acct = {
                "id": acct_id,
                "serviceID": ext_id,
                "description": "default",
                "credential": {"type": "api", "key": actual_key},
            }
            old_acct = accounts.get(acct_id, {})
            if old_acct != new_acct:
                account_changes[acct_id] = new_acct

            if active.get(ext_id) != acct_id:
                active_changes[ext_id] = acct_id

    disabled_prefixes = set()
    for base_id in active_extensions:
        disabled_prefixes.add(f"{base_id}-")

    active_service_ids = {f"{base_id}-{suffix}"
                          for base_id, suffixes in active_extensions.items()
                          for suffix in suffixes}
    stale_accounts = set()
    for aid, acct in accounts.items():
        sid = acct.get("serviceID", "")
        is_managed = any(sid.startswith(p) for p in disabled_prefixes)
        if is_managed and sid not in active_service_ids:
            stale_accounts.add(aid)

    stale_active = {k for k in active
                    if any(k.startswith(p) for p in disabled_prefixes)
                    and k not in {f"{b}-{s}" for b, ss in active_extensions.items() for s in ss}}

    if dry_run:
        for aid in sorted(account_changes):
            print(f"  account +{aid}: {account_changes[aid]['serviceID']}")
        for sid in sorted(active_changes):
            print(f"  active +{sid}: {active_changes[sid]}")
        for aid in sorted(stale_accounts):
            a = accounts[aid]
            print(f"  account -{aid}: {a.get('serviceID', '?')}")
        for sid in sorted(stale_active):
            print(f"  active -{sid}")
        return bool(account_changes or active_changes or stale_accounts or stale_active)

    for aid in stale_accounts:
        accounts.pop(aid, None)
    for sid in stale_active:
        active.pop(sid, None)
    accounts.update(account_changes)
    active.update(active_changes)
    target["accounts"] = accounts
    target["active"] = active
    return bool(account_changes or active_changes or stale_accounts or stale_active)

def main():
    parser = argparse.ArgumentParser(description="Sync SSOT provider configs to extended providers in opencode.json")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--ssot", help="Path to SSOT models.json (default: opencode/cache/models.json)")
    parser.add_argument("--extensions", help="Path to provider extensions file (default: scripts/provider-extensions.json)")
    parser.add_argument("--config", help="Path to target opencode.json (default: opencode/config/opencode.json)")
    parser.add_argument("--auth", help="Path to auth.json (default: opencode/share/auth.json)")
    parser.add_argument("--account", help="Path to account.json (default: opencode/share/account.json)")
    parser.add_argument("--keywords", required=True, help="Path to the key-value file")
    args = parser.parse_args()

    ssot_path = Path(args.ssot) if args.ssot else CACHE_FILE
    ext_path = Path(args.extensions) if args.extensions else EXTENSIONS_FILE
    config_path = Path(args.config) if args.config else CONFIG_FILE
    auth_path = Path(args.auth) if args.auth else AUTH_FILE
    account_path = Path(args.account) if args.account else ACCOUNT_FILE
    keywords_path = Path(args.keywords)

    print(f"Reading SSOT: {ssot_path}")
    with open(ssot_path) as f:
        ssot = json.load(f)

    print(f"Reading extensions: {ext_path}")
    with open(ext_path) as f:
        raw_extensions = json.load(f)

    print(f"Reading config: {config_path}")
    with open(config_path) as f:
        config = json.load(f)

    print(f"Reading auth: {auth_path}")
    with open(auth_path) as f:
        auth = json.load(f)

    print(f"Reading account: {account_path}")
    with open(account_path) as f:
        account = json.load(f)

    print(f"Reading keywords: {keywords_path}")
    keywords = parse_keywords(keywords_path)

    active_extensions, disabled_ids, key_map = parse_extensions(raw_extensions)
    existing_providers = config.get("provider", {})

    print("Building extended providers...")
    new_providers = build_providers(ssot, active_extensions)

    ext_prefixes = {f"{base_id}-" for base_id in {**active_extensions}}
    managed = {k for k in existing_providers
               if any(k.startswith(p) for p in ext_prefixes)}

    kept = {k: v for k, v in existing_providers.items() if k not in managed}
    removed = managed - set(new_providers)
    updated = {}
    changed = set()
    for pid, new_val in new_providers.items():
        existing = existing_providers.get(pid, {})
        merged = existing | new_val
        updated[pid] = merged
        if existing != merged:
            changed.add(pid)

    updated = kept | updated
    has_config_changes = bool(changed or removed)

    if args.dry_run:
        print()
        if has_config_changes:
            print(f"[Dry Run] Would update {len(changed)} provider(s):")
            for pid in sorted(changed):
                p = new_providers[pid]
                print(f"  + {pid}: env={p['env']}, name={p['name']}")
            if removed:
                print(f"  [remove] {', '.join(sorted(removed))}")
        else:
            print("[Dry Run] Config is up to date.")

        print()
        print("[Dry Run] Auth changes:")
        auth_changed = sync_auth(auth, active_extensions, key_map, keywords, dry_run=True)
        print()
        print("[Dry Run] Account changes:")
        acct_changed = sync_accounts(account, active_extensions, key_map, keywords, dry_run=True)
        if not auth_changed and not acct_changed and not has_config_changes:
            print("Everything up to date.")
        return

    if has_config_changes:
        config["provider"] = updated
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
            f.write("\n")
        for pid in sorted(changed):
            p = new_providers[pid]
            print(f"  + {pid}: env={p['env']}, name={p['name']}")
        if removed:
            print(f"  - {', '.join(sorted(removed))}")
        print(f"Synced config to {config_path}")
    else:
        print("Config up to date.")

    auth_result = sync_auth(auth, active_extensions, key_map, keywords, dry_run=False)
    if auth_result:
        with open(auth_path, "w") as f:
            json.dump(auth, f, indent=2)
            f.write("\n")
        print(f"Synced auth to {auth_path}")
    else:
        print("Auth up to date.")

    acct_result = sync_accounts(account, active_extensions, key_map, keywords, dry_run=False)
    if acct_result:
        with open(account_path, "w") as f:
            json.dump(account, f, indent=2)
            f.write("\n")
        print(f"Synced account to {account_path}")
    else:
        print("Account up to date.")

if __name__ == "__main__":
    main()
