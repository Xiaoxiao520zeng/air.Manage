# 项目负责人使用指南

这个仓库的作用是让工作进展可回看、问题能被发现、团队经验能留下来。负责人不需要逐字检查每条流水账，主要关注提交情况、结果、风险和需要协助的事项。

## 初始化团队

1. 在 [`../team/team-overview.md`](../team/team-overview.md) 填团队方向、目标、分工和协作约定。
2. 在 [`../team/members.txt`](../team/members.txt) 每行填写一个成员的固定名称。名称要和大家创建文件时使用的 `--name` 完全一致。
3. 在 [`../blackboard/rotation.md`](../blackboard/rotation.md) 安排知识分享轮值。
4. 确认成员能读取仓库并有提交权限，把[成员使用指南](team-member-guide.md)发给团队。

团队资料和工作总结都对仓库成员可见。这里不要放个人隐私、密码或访问令牌。

## 每天看什么

在仓库根目录运行：

```bash
python3 tools/summary.py check missing-daily
python3 tools/summary.py check daily
```

第一条列出名单中还没交日总结的人；第二条检查当天已提交的总结有没有漏填栏目。然后重点阅读：

- **今日完成**：是否有可确认的结果，是否影响项目目标。
- **遇到的问题**：有没有阻塞、风险、外部依赖或明确的协助请求；安排负责人和后续跟进。
- **明日计划**：是否与项目当前优先级一致。

缺交检查只有在 `team/members.txt` 填好后才有用。有人还没到提交时间时，缺交名单只是提醒，不代表工作没有完成。

## 每周看什么

```bash
python3 tools/summary.py check missing-weekly
python3 tools/summary.py check weekly
```

阅读每个人的本周完成、本周收获、问题和下周计划。把注意力放在：本周目标完成情况、连续几周未解决的阻塞、成员之间的依赖、下周计划是否过多，以及是否需要调整资源或优先级。

负责人可以把需要继续跟进的事项写进项目管理系统或会议记录，并在下一次总结中回看结果。当前仓库不会自动生成风险趋势或提醒。

## 管理知识黑板

按 [`../blackboard/rotation.md`](../blackboard/rotation.md) 安排成员轮流分享。确认每份分享都包括清楚的主题、适用场景、关键步骤和示例/练习。鼓励其他成员在 Pull Request 中提出问题或补充经验；有长期价值的补充再合并回分享文档。

## 审核和合并

建议成员用分支和 Pull Request 提交。负责人审核时先看自动检查是否通过，再确认文件日期、作者、栏目是否完整、内容是否适合团队共享。自动检查只验证日/周总结栏目非空，不评价内容质量，也不检查是否泄露敏感信息；负责人仍需做人工检查。

检查通过后合并到 `main`。如果团队希望所有记录必须经负责人审核，可在 GitHub 仓库设置 `main` 分支保护，要求 Pull Request 和检查通过后才能合并。这个保护规则需要在 GitHub 设置中启用；当前仓库尚未配置。

## 常用目录

- `team/team-overview.md`：团队目标、分工和协作约定。
- `team/members.txt`：用于缺交检查的成员名单。
- `summaries/日期/`：每日总结。
- `summaries/weekly/年-W周次/`：每周总结。
- `blackboard/`：知识分享和轮值安排。
- `docs/team-member-guide.md`：成员操作说明。
