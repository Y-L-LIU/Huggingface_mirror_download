"""
Construct metalink file from huggingface(-like) HTML responses
"""

import re
from argparse import ArgumentParser

import requests
from tqdm import tqdm


def _main():
    parser = ArgumentParser()
    parser.add_argument("org_repo")
    parser.add_argument("--timeout", type=float, default=5)
    parser.add_argument("--endpoint", type=str, default="hf-mirror.com")
    parser.add_argument("--output", "-O", type=str, default=None)
    args = parser.parse_args()
    timeout = args.timeout
    endpoint = args.endpoint
    org, repo = args.org_repo.split("/")
    print(f"Got repo: org={org}, repo={repo}")

    resp = requests.get(f"https://{endpoint}/{org}/{repo}/tree/main", timeout=timeout)

    filenames = re.findall(
        rf"/{org}/{repo}/resolve/main/([^\?]+)\?download=true", resp.text
    )
    for fn in filenames:
        print(f"Got filename: {fn}")

    resps = [
        requests.get(
            f"https://{endpoint}/{org}/{repo}/raw/main/{fn}",
            timeout=timeout,
        )
        for fn in tqdm(filenames, desc="Fetching SHA256 checksums")
    ]

    hash_matches = [re.search(r"sha256:([a-z0-9]{64})", resp.text) for resp in resps]
    for fn, m in zip(filenames, hash_matches):
        if m is not None:
            print(f"Got sha256 for filename={fn}: sha256={m.group(1)}")

    verifies = [
        f"""
<verification>
    <hash type="sha256">{m.group(1)}</hash>
</verification>"""
        if m is not None
        else ""
        for m in hash_matches
    ]

    files = "\n".join(
        [
            f"""<file name="{fn}">{verify}
<resources>
    <url type="https">https://{endpoint}/{org}/{repo}/resolve/main/{fn}?download=true</url> 
</resources>
</file>"""
            for fn, verify in zip(filenames, verifies)
        ]
    )

    fn_output = f"{repo}.metalink" if args.output is None else args.output

    # %%
    with open(fn_output, "w", encoding="utf-8") as f:
        f.write(
            f"""<metalink version="3.0" xmlns="http://www.metalinker.org/">
<files>{files}
</files>
</metalink>"""
        )


if __name__ == "__main__":
    _main()
