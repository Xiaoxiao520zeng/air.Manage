#!/usr/bin/env python3
"""Create and check shared daily, weekly, and knowledge-sharing notes."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMBERS_FILE = ROOT / "team" / "members.txt"
SECTIONS = {
    "daily": ("今日完成", "遇到的问题", "明日计划"),
    "weekly": ("本周完成", "本周收获", "遇到的问题", "下周计划"),
    "board": ("分享主题", "适用场景", "关键步骤", "示例或练习"),
}


def parse_day(value: str | None) -> date:
    if value is None:
        return date.today()
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("日期请使用 YYYY-MM-DD 格式") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("日期请使用 YYYY-MM-DD 格式")
    return parsed


def safe_name(value: str) -> str:
    name = value.strip()
    if not name or name in {".", ".."} or any(c in name for c in "/\\\0"):
        raise argparse.ArgumentTypeError("姓名不能为空，也不能包含路径字符")
    return name


def daily_template(name: str, day: date) -> str:
    return f"""# {day.isoformat()} 工作总结 · {name}

## 今日完成

- 

## 遇到的问题

- 无

## 明日计划

- 
"""


def weekly_template(name: str, day: date) -> tuple[str, str]:
    year, week, _ = day.isocalendar()
    start = date.fromisocalendar(year, week, 1)
    end = start + timedelta(days=6)
    period = f"{year}-W{week:02d}"
    content = f"""# {period} 周总结 · {name}

总结周期：{start.isoformat()} 至 {end.isoformat()}

## 本周完成

- 

## 本周收获

- 

## 遇到的问题

- 无

## 下周计划

- 
"""
    return period, content


def board_template(name: str, day: date) -> str:
    return f"""# 知识黑板 · {day.isoformat()} · {name}

## 分享主题

<!-- 这次希望团队学会什么？ -->

## 适用场景

<!-- 什么时候会用到这项知识？ -->

## 关键步骤

1. 

## 示例或练习

<!-- 给出一个能跟着做的例子或练习。 -->

## 讨论与补充

<!-- 留给其他成员的问题、经验和补充。 -->
"""


def create(kind: str, name: str, day: date) -> int:
    if kind == "daily":
        relative = Path("summaries") / day.isoformat() / f"{name}.md"
        content = daily_template(name, day)
    elif kind == "weekly":
        period, content = weekly_template(name, day)
        relative = Path("summaries") / "weekly" / period / f"{name}.md"
    else:
        relative = Path("blackboard") / f"{day.isoformat()}-{name}.md"
        content = board_template(name, day)

    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"已存在：{relative}", file=sys.stderr)
        return 1
    path.write_text(content, encoding="utf-8")
    print(relative)
    return 0


def record_files(kind: str) -> list[Path]:
    if kind == "daily":
        return sorted((ROOT / "summaries").glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/*.md"))
    if kind == "weekly":
        return sorted((ROOT / "summaries" / "weekly").glob("[0-9][0-9][0-9][0-9]-W[0-9][0-9]/*.md"))
    if kind == "board":
        return sorted((ROOT / "blackboard").glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*.md"))
    return record_files("daily") + record_files("weekly") + record_files("board")


def validate_files(files: list[Path], kind: str) -> int:
    if not files:
        print("没有找到可检查的总结", file=sys.stderr)
        return 1

    errors: list[str] = []
    for path in files:
        content = path.read_text(encoding="utf-8")
        for section in SECTIONS[kind]:
            match = re.search(rf"^##\s+{re.escape(section)}\s*$([\s\S]*?)(?=^##\s|\Z)", content, re.M)
            body = match.group(1).strip() if match else ""
            body = re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()
            if not body or body in {"-", "待填写"}:
                errors.append(f"{path.relative_to(ROOT)}：请填写“{section}”")

    if errors:
        print("检查未通过：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"检查通过：{len(files)} 份总结")
    return 0


def kind_for_path(path: Path) -> str | None:
    parts = path.parts
    if "blackboard" in parts:
        return "board"
    if "summaries" in parts:
        if "weekly" in parts:
            return "weekly"
        return "daily"
    return None


def check_files(raw_paths: list[str]) -> int:
    grouped: dict[str, list[Path]] = {}
    for raw in raw_paths:
        path = Path(raw)
        if not path.is_absolute():
            path = ROOT / path
        kind = kind_for_path(path)
        if kind is None or path.suffix != ".md" or not path.is_file():
            continue
        grouped.setdefault(kind, []).append(path)

    if not grouped:
        print("没有需要检查的总结文件")
        return 0

    errors = 0
    for kind in ("daily", "weekly", "board"):
        if kind in grouped:
            errors += validate_files(sorted(grouped[kind]), kind)
    return 1 if errors else 0


def check_day(kind: str, day: date) -> int:
    if kind == "daily":
        folder = ROOT / "summaries" / day.isoformat()
        label = day.isoformat()
    else:
        year, week, _ = day.isocalendar()
        label = f"{year}-W{week:02d}"
        folder = ROOT / "summaries" / "weekly" / label
    if not folder.is_dir():
        print(f"没有找到 {label} 的总结目录", file=sys.stderr)
        return 1
    return validate_files(sorted(folder.glob("*.md")), kind)


def check_missing(kind: str, day: date) -> int:
    if not MEMBERS_FILE.is_file():
        print("没有团队名单，请先填写 team/members.txt", file=sys.stderr)
        return 1
    members = [line.strip() for line in MEMBERS_FILE.read_text(encoding="utf-8").splitlines()
               if line.strip() and not line.lstrip().startswith("#")]
    if not members:
        print("团队名单为空，请先在 team/members.txt 中每行填写一位成员", file=sys.stderr)
        return 1

    if kind == "daily":
        folder = ROOT / "summaries" / day.isoformat()
        label = day.isoformat()
    else:
        year, week, _ = day.isocalendar()
        label = f"{year}-W{week:02d}"
        folder = ROOT / "summaries" / "weekly" / label
    present = {path.stem for path in folder.glob("*.md")} if folder.is_dir() else set()
    missing = [member for member in members if member not in present]
    if missing:
        print(f"{label} 尚未提交：" + "、".join(missing))
        return 1
    print(f"{label} 全员已提交（{len(members)} 人）")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="团队工作总结与知识分享工具")
    commands = parser.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new", help="创建一份记录模板")
    new.add_argument("kind", choices=("daily", "weekly", "board"), help="daily 日总结、weekly 周总结、board 知识黑板分享")
    new.add_argument("--name", required=True, type=safe_name, help="姓名或团队约定的用户名")
    new.add_argument("--date", help="日期 YYYY-MM-DD；默认今天，周总结按该日期所在周归档")

    verify = commands.add_parser("check", help="检查总结内容或成员提交情况")
    verify.add_argument("kind", choices=("daily", "weekly", "all", "files", "missing-daily", "missing-weekly"))
    verify.add_argument("--date", help="日期 YYYY-MM-DD；默认今天")
    verify.add_argument("paths", nargs="*", help="kind=files 时，要检查的文件路径（相对仓库根目录）")

    args = parser.parse_args()
    try:
        day = parse_day(args.date)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    if args.command == "new":
        return create(args.kind, args.name, day)
    if args.kind == "files":
        return check_files(args.paths)
    if args.kind == "all":
        errors = 0
        checked = 0
        for kind in ("daily", "weekly", "board"):
            files = record_files(kind)
            if files:
                checked += len(files)
                errors += validate_files(files, kind)
        if not checked:
            print("当前没有总结需要检查")
            return 0
        return 1 if errors else 0
    if args.kind.startswith("missing-"):
        return check_missing(args.kind.removeprefix("missing-"), day)
    return check_day(args.kind, day)


if __name__ == "__main__":
    raise SystemExit(main())
