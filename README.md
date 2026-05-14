# 视频复刻拆解 Skill

这是一个 Codex skill，用来把值得模仿的视频拆成可复刻的创作蓝图。

它和 `watch-video` 是两份不同工作：

- `watch-video`：看懂总结，回答视频讲了什么、是否靠谱、对你有什么启发。
- `video-replication-breakdown`：复刻拆解，回答这个视频为什么有效、怎么拍、怎么剪、怎么改成你的版本。

## 能做到什么

- 真实读取视频、抖音/TikTok 图文、录屏或网页视频证据。
- 拆解开头钩子、叙事结构、镜头功能、剪辑节奏、字幕和声音。
- 生成分镜时间线、镜头功能表、风格层分析和素材映射。
- 输出可执行的复刻脚本和 AI 生成提示词。
- 生成 HTML 案例拆解页，用来承载截图、分镜、ASR、脚本、提示词和本地资产路径。

## 适合什么时候用

- “拆解这个视频，让我也能复刻。”
- “这个爆款视频怎么拍出来？”
- “帮我提取分镜、脚本和提示词。”
- “我想模仿这个视频结构，但换成我的主题。”
- “把这个视频整理成 HTML 案例资产页。”

不适合：

- “这个视频讲了什么？”
- “这个观点靠谱吗？”
- “对我有什么启发，我该怎么做？”

这些问题请用 `watch-video`。

## 安装

在另一台电脑上通过 skill-installer 安装：

```text
https://github.com/huojiaheng123-cpu/video-replication-breakdown-skill
```

为了达到和我本地一样的效果，建议同时安装看懂总结底座：

```text
https://github.com/huojiaheng123-cpu/watch-video-skill
```

## 使用示例

```text
帮我拆解这个视频，让我也能复刻一个同结构的视频。
```

Codex 应该先读取证据，再输出复刻价值、分镜时间线、风格层分析、复刻脚本、AI 提示词和 HTML 案例报告。

## 主要文件

- `SKILL.md`：skill 使用说明。
- `references/report-structure.md`：HTML 报告栏目和质量门槛。
- `assets/html-report-template.html`：HTML 案例拆解页模板。
- `agents/openai.yaml`：Codex UI metadata。
