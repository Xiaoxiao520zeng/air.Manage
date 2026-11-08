# 团队工作总结与知识分享

一个基于 Markdown 和 Git 的轻量工具，不包含网站或后台服务。

## 记录类型

- **每日总结**：所有成员可见，按天归档。
- **每周总结**：所有成员可见，按 ISO 周次归档。
- **知识黑板**：成员轮流分享已掌握的知识，其他成员可查看并补充讨论。

仓库的读取权限作用于整个仓库：所有有读取权限的成员都能查看其中的文件和 Git 历史。请勿提交密码、访问令牌或其他凭据。

## 创建记录

```bash
python3 tools/summary.py new daily --name 张三
python3 tools/summary.py new weekly --name 张三
python3 tools/summary.py new board --name 张三
```

按需填写指定日期；周总结会自动放进该日期所属的 ISO 周目录：

```bash
python3 tools/summary.py new daily --name 张三 --date 2026-11-08
python3 tools/summary.py new weekly --name 张三 --date 2026-11-08
```

脚本会打印新文件路径。用编辑器填写后，成员提交自己的记录：

```bash
git add summaries/ blackboard/
git commit -m "docs: add daily summary"
git push
```

## 检查与团队名单

先在 [`team/members.txt`](team/members.txt) 每行填写一位成员，名称要与创建总结时的 `--name` 一致。负责人可检查当天或当周的栏目，也可以查看谁还没提交：

```bash
python3 tools/summary.py check daily
python3 tools/summary.py check weekly
python3 tools/summary.py check missing-daily
python3 tools/summary.py check missing-weekly
```

指定日期（周总结按该日期所在的 ISO 周检查）：

```bash
python3 tools/summary.py check missing-daily --date 2026-11-08
```

每次提交到 GitHub 或创建 Pull Request 时，自动检查会验证所有日总结和周总结的必填栏目。名单检查不会放进自动流程，因为当天提交过程中可能有人还没来得及提交。

所有工具只依赖 Python 标准库，不会替成员提交或推送。知识黑板轮值顺序和说明见 [`blackboard/rotation.md`](blackboard/rotation.md)。
