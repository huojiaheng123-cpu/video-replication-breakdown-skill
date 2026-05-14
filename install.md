# video-replication-breakdown 安装与 full 能力升级

这个 Skill 的目标不是“复制文件后立刻满血”，而是让 Codex 能在不同电脑、不同插件、不同依赖状态下，先体检缺口，再一步步补到和原本本地环境一致的效果。

## 能力等级

- `minimal`：只有复刻拆解说明和 HTML 模板，不能声称已完整读取视频证据。
- `recommended`：已安装 `watch-video`，能生成 HTML 案例页，但证据能力可能不完整。
- `full`：`watch-video` 已达到 full，当前 Skill 模板/报告结构完整，`00_工作台` 可写，能输出证据齐全的 HTML 复刻案例页、分镜、脚本和提示词。

## 第一步：安装两个 Skill

先安装复刻拆解 Skill：

```text
https://github.com/huojiaheng123-cpu/video-replication-breakdown-skill
```

再安装证据底座 Skill：

```text
https://github.com/huojiaheng123-cpu/watch-video-skill
```

安装后重启 Codex。

## 第二步：体检当前环境

在本 Skill 目录运行：

```bash
python scripts/check_capabilities.py
```

它会检查：

- `watch-video` 是否安装。
- `watch-video` 是否已经是 `full`。
- HTML 报告模板和结构参考是否存在。
- 当前工作区的 `00_工作台` 是否可写。
- Node/npm 是否可用。
- 是否能检测到 Browser/browser-use 插件。

## 第三步：自动补本地依赖

运行：

```bash
python scripts/setup_full.py
```

它会：

- 安装本 Skill 的本地依赖。
- 自动寻找 `watch-video`。
- 如果找到 `watch-video`，调用它的 `scripts/setup_full.py` 补齐 FFmpeg/Playwright/转写相关依赖中可自动安装的部分。
- 重新运行体检。

它不会静默安装：

- Codex Browser 插件。
- FFmpeg / Chrome / Edge 等系统软件。
- 用户账号级连接器或插件。

这些项目必须由用户确认安装。

## 第四步：把 watch-video 拉到 full

进入 `watch-video` Skill 目录，反复执行：

```bash
python scripts/check_capabilities.py
python scripts/setup_full.py
```

如果仍然缺系统软件或插件，按输出提示手动补齐，再重启 Codex。

## 第五步：验证复刻能力

回到本 Skill 目录运行：

```bash
python scripts/check_capabilities.py
```

看到 `Current video-replication-breakdown capability level: full` 后，才代表能稳定达到原本本地环境的复刻拆解效果。

## 给同事的 setup prompt

```text
请帮我安装并升级 video-replication-breakdown-skill 到 full 能力。它依赖 watch-video-skill 做证据底座。请先分别安装这两个 GitHub skill，重启 Codex，然后运行 video-replication-breakdown 的 scripts/check_capabilities.py。缺本地依赖就运行 scripts/setup_full.py；如果缺 FFmpeg、Chrome/Edge 或 Browser 插件，请一步步引导我手动安装/启用。每完成一步都重新检测，直到 video-replication-breakdown 和 watch-video 都达到 full，或明确说明还差什么以及降级后会影响哪些能力。
```

## full 前的使用边界

如果没有达到 `full`，Codex 必须在交付中说明证据边界：

- 缺 `watch-video`：不能做完整视频证据读取，只能做静态/文本级复刻建议。
- `watch-video` 不是 full：复刻报告必须标明哪些证据未确认。
- 缺 Browser 插件：不能直接用 Codex 交互预览网页/本地 HTML，只能用文件和脚本验证。
- 缺 FFmpeg/ffprobe：不能可靠抽帧、读媒体信息或提取音频。
- 缺转写能力：不能把口播作为已确认证据，只能基于字幕/画面/人工文本推断。
