# YOLOv8 绝缘子检测项目卡片（贾明泽）

项目现状速查，便于新成员快速接手；数据已与项目内 `docs\05_项目现状.md` 核对（截至 2026-11-07 暂停点）。

## 一句话

输电线路**绝缘子缺陷检测**：三类（绝缘子 / 破损 / 闪络），已跑通「相机端推理 + 电脑端看结果」，验证集 mAP50 = **0.835**；**真实场景的小破损仍是最大短板**。

## 环境

- 路径：`D:\deep seek harness\yolov8`，独立 `.venv`（3.6 GB，别删别挪）
- torch 2.15.0+cu132 / ultralytics 8.4.202 / depthai 3.12.0
- 显卡 RTX 5060 Ti 8 GB（sm_120），YOLOv8n 单张推理 ~6 ms
- **只有命令行，没有网页界面**。所有「窗口」都是 .bat 拉起的控制台 + OpenCV imshow

## 入口（双击即用）

| 文件 | 算力在哪 | 帧率 | 用途 |
| --- | --- | --- | --- |
| `端侧测试.bat` | 相机芯片（RVC2） | 12~13 | 快速扫视、讲流程 |
| `精准模式.bat` | 相机 + 显卡两级 | 7~8 | **找小破损，演示首选** |
| `摄像头实时.bat` | 电脑显卡 | 16 | 老版本对照 |
| `高置信演示.bat` | 电脑显卡 conf≥0.6 | 16 | 数字好看版 |
| `打开命令行.bat` | — | — | 手敲命令 |

`打开命令行.bat` 会调 `start.ps1` 激活环境（`start.ps1` 别直接双击）。

## 模型版本

| 版本 | 目录 | 类别 | mAP50 | 说明 |
| --- | --- | --- | --- | --- |
| v1 | `runs\train\insulator_v8n` | 2 | 0.991 | 缺陷是合成图，虚高 |
| v2 | `runs\train\v2_base` | 2 | 0.800 | 第一版真实数据 |
| v2-T | `runs\train\v2_necktr` | 2 | 0.795 | Neck 换 C3TR，**无收益、显存 +86%** |
| v3 | `runs\train\v3_base` | 2 | 0.802 | 标签有污染 |
| **v4** | **`runs\train\v4_base`** | **3** | **0.835** | **现役** |
| v5 | `runs\train\v5_neg` | 3 | 0.805 | +90 负样本，误检 0/30，仅备份 |

v4 分类别：insulator 0.946 / broken 0.839 / flashover 0.719（mAP50）。

## 关键路径

```
权重    runs\train\v4_base\weights\best.pt
blob    blobs\best_openvino_2022.1_6shave.blob      （640，端侧默认）
        blobs\best960_openvino_2022.1_6shave.blob   （960，慢 4 倍）
成绩单  runs\live_metrics_v4.json
记录    records\edge_*.jsonl + records\shots\*.jpg（文件名带类别和置信度）
报告    docs\01_数据集核查报告.md  docs\02_AB对照报告.md  docs\03_v3数据扩充与切片实验.md
        docs\04_端侧部署.md  docs\05_项目现状.md
```

## 两级识别（精准模式）为什么必要

640×640 输入，最细特征图 20×20 → **目标 <10 像素基本看不见**。

```
一级：全图找「整串」   → 破损被压到 13 像素，漏（0 个）
二级：裁出整串再放大   → 破损变 40+ 像素，检出（5 个）
```

## 已知问题（别当新发现）

1. 小破损短板：真实缺陷（国内瓷件、复合伞裙）训练数据没覆盖
2. USB2 链路：设备名 `1.x` = USB2，预览 12~15 fps 天花板（`3.x` 才是 USB3）
3. RVC2 算力上限：640 约 13 fps、960 约 4~5 fps
4. 域外误检：人头/椅子被框成绝缘子，v5 负样本可压到 0/30
5. 竖直绝缘子串检出率低于水平（训练集以横向为主）

## 下次做什么

| 优先级 | 事情 | 耗时 |
| --- | --- | --- |
| 高 | 补真实破损数据，重训 v6 | 看数据 |
| 中 | 训专用二级模型（只喂裁剪后的整串图）替换借用 v4 | 2~3 h |
| 低 | 换 USB3 线，预览拉到 30 fps | 10 min |

## 环境坑

- 本机代理 `127.0.0.1:7897`：ultralytics 自动下载数据集会走代理被掐断 → 先 `$env:NO_PROXY="*"`
- Windows 多进程读数据会卡死 → 脚本里 `workers=0`
- 8 GB 显存：`yolov8n` + `batch 8~16` + `imgsz 640` 最稳
- `device=0` 是显卡，`device="cpu"` 慢几十倍
- 中文乱码：bat 里已 `set PYTHONIOENCODING=gbk`；手动跑 python 时设 `utf-8`
- DSH 沙箱里跑训练会报「命名管道 Permission denied」→ 要在用户自己的 PowerShell 里跑
- `.bat` 里设了 `LOCALAPPDATA=%~dp0.appdata`，避免往系统目录写缓存

## 理论笔记

整理在 `C:\Users\Admin\Desktop\每日学习\yolov8-手写笔记-2026-11-09.md`（含对「YOLOv8 + Transformer」的修正），原图存档 `notes\assets\2026-11-09-yolov8-handnote.jpg`。
