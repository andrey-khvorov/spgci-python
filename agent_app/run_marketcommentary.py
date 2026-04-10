from __future__ import annotations

import argparse

import spgci as ci
import spgci.config as cfg

from agent_app.lib.skill_loader import load_skill_markdown


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Minimal agent emulator: load skill doc from repo and execute Market Commentary"
    )
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--token", default=None)
    parser.add_argument("--phrase", default=None)
    parser.add_argument("--template", default=None)
    parser.add_argument("--from-date", required=True)
    parser.add_argument("--to-date", required=True)
    parser.add_argument("--limit", type=int, default=120)
    args = parser.parse_args()

    # 1) Load skill doc from the repo (NOT from the API)
    md = load_skill_markdown("marketcommentary")
    print("--- Loaded skill doc from repo ---")
    print("\n".join(md.splitlines()))

    # 2) Configure client
    cfg.base_url = args.base_url
    if args.token:
        cfg.set_token(args.token)

    print(f"\nbase_url={cfg.base_url}")

    # 3) Execute skill steps
    print("\n--- Step 1: list templates ---")
    templates_df = ci.market_commentary.list_templates(phrase=args.phrase)
    print(templates_df.head(10))

    if len(templates_df) == 0:
        print("\nNo templates returned; cannot proceed to read.")
        return 2

    template = args.template or templates_df.loc[0, "template"]
    print(f"\n--- Step 2: read commentary (template={template!r}) ---")
    df = ci.MarketCommentary().get_market_commentaries(
        templates=[template],
        from_date=args.from_date,
        to_date=args.to_date,
        limit=args.limit,
    )
    print(df.head(10))

    meta = df.attrs.get("spgci_market_commentary")
    if meta:
        print("\n--- Response meta ---")
        print(meta)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
