# 团队成员使用指南

这份仓库用来记录每天和每周的工作，以及轮流分享团队知识。所有记录都是普通 Markdown 文件，提交到 GitHub 后，拥有仓库读取权限的成员都能查看。

## 第一次使用

你需要：

- 已安装 Git。
- Python 3.10 或更新版本，不需要安装第三方 Python 包。
- 负责人已给你 GitHub 仓库访问和推送权限。

克隆仓库并进入目录：

```bash
git clone https://github.com/Xiaoxiao520zeng/air.Manage.git
cd air.Manage
```

使用 Windows PowerShell 时，如果 `python3` 命令不存在，可将下面命令里的 `python3` 换成 `py -3`。

## 每天写工作总结

开始前先同步仓库，避免基于过期内容提交：

```bash
git switch main
git pull --ff-only
```

创建今天的总结：

```bash
python3 tools/summary.py new daily --name 张三
```

把“张三”换成团队名单中自己的固定名称。工具会打印文件路径，通常是 `summaries/2026-11-08/张三.md`。打开这个文件，填写：

- **今日完成**：写做了什么，以及结果是什么。尽量具体，例如“完成登录接口联调，修复验证码过期问题”。
- **遇到的问题**：写阻塞、风险或需要谁协助；没有就保留“无”。
- **明日计划**：写下一步准备做的事。

把示例空行 `-` 替换成实际内容。完成后检查当天总结：

```bash
python3 tools/summary.py check daily
```

如果补写其他日期，可在创建和检查命令后加 `--date YYYY-MM-DD`：

```bash
python3 tools/summary.py new daily --name 张三 --date 2026-11-07
python3 tools/summary.py check daily --date 2026-11-07
```

## 写每周总结

每周总结把一周的工作整理成整体结果，不需要把每天的内容原样复制。运行：

```bash
python3 tools/summary.py new weekly --name 张三
```

周总结会按 ISO 周次放到 `summaries/weekly/YYYY-Www/`，例如 `summaries/weekly/2026-W46/张三.md`。填写本周完成、本周收获、遇到的问题和下周计划。检查本周内容：

```bash
python3 tools/summary.py check weekly
```

## 轮到你时分享知识黑板

查看 [`../blackboard/rotation.md`](../blackboard/rotation.md) 确认轮值安排。轮到你时运行：

```bash
python3 tools/summary.py new board --name 张三
```

在生成的 `blackboard/YYYY-MM-DD-张三.md` 中写清楚分享主题、适用场景、关键步骤，并给出一个示例或练习。内容以其他成员能照着理解和尝试为准。分享后，其他成员可以通过 Pull Request 在“讨论与补充”里添加问题或经验。

## 提交到 GitHub

建议每次总结使用一个单独分支，再通过 Pull Request 合并到 `main`。例如提交今天的日总结：

```bash
git switch -c summary/2026-11-08-zhangsan
git add summaries/2026-11-08/张三.md
git commit -m "docs: daily summary 2026-11-08 zhangsan"
git push -u origin summary/2026-11-08-zhangsan
```

推送后，在 GitHub 仓库页面创建 Pull Request，目标分支选 `main`。等待自动检查完成，再按团队约定请求负责人审核和合并。每次提交应只包含自己的总结或负责的知识分享，方便检查。

如果团队允许直接推送 `main`，可在负责人说明后跳过建分支和 Pull Request，直接提交；多人协作仍建议使用 Pull Request。

## 查看谁还没提交

负责人维护 [`../team/members.txt`](../team/members.txt)，每行一个成员名称。名称必须与大家命令里的 `--name` 和文件名完全一致。名单设置好后，负责人可运行：

```bash
python3 tools/summary.py check missing-daily
python3 tools/summary.py check missing-weekly
```

日/周总结栏目的自动检查会在 Pull Request 中运行。缺交检查是人工运行的，因为当天可能还有成员正在撰写。

## 注意事项

- 总结和知识分享对所有仓库成员可见，Git 历史也会保留旧版本；不要提交密码、访问令牌或不适合团队共享的信息。
- 不要直接改写或删除其他成员的总结；有补充建议时，通过 Pull Request 评论沟通。
- 同一成员同一天只创建一份日总结。如果提示文件已存在，就打开原文件补充，不要另起重名文件。
- 补交或更正内容时，使用原来的日期和文件，并在提交说明中写清楚更正原因。
