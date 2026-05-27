import argparse
import sys


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def decide_stage(goal: str, has_scope: bool, has_constraints: bool, has_spec: bool) -> tuple[str, str]:
    if not goal.strip():
        return "brief", "缺少明确目标，先整理需求卡片。"
    if not has_scope or not has_constraints:
        return "brief", "范围或约束仍不完整，先补 brief。"
    if not has_spec:
        return "spec", "brief 已具备最小条件，下一步进入 spec。"
    return "build", "brief 和 spec 已明确，可以开始实现。"


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend the next VibeFoundry stage.")
    parser.add_argument("--goal", default="", help="Task goal in plain text.")
    parser.add_argument("--has-scope", action="store_true", help="Whether scope is defined.")
    parser.add_argument("--has-constraints", action="store_true", help="Whether constraints are defined.")
    parser.add_argument("--has-spec", action="store_true", help="Whether a spec already exists.")
    args = parser.parse_args()

    stage, reason = decide_stage(
        goal=args.goal,
        has_scope=args.has_scope,
        has_constraints=args.has_constraints,
        has_spec=args.has_spec,
    )
    print(f"next_stage={stage}")
    print(f"reason={reason}")


if __name__ == "__main__":
    main()
