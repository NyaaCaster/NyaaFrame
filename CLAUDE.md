# NyaaFrame — Claude Code 项目规则

## 项目概述

NyaaFrame 是一个标准开发环境模板项目，用于快速启动 WebApp 和轻量服务开发。

- 堆栈：Nginx + Vite + React + TypeScript + Tailwind
- 容器化：Docker（多阶段构建，最小体积）
- 仓库：https://github.com/NyaaCaster/NyaaFrame.git
- 主分支：master

## 交流语言

默认始终以**简体中文**与用户交流，除非用户在某次对话中明确要求改用其他语言。

- 适用范围：所有面向用户的文字输出（解释、总结、提问、错误说明等）。
- 代码、标识符、命令行参数、文件路径、提交信息等仍按惯例使用英文。
- 即使用户的某条消息使用了英文，默认回复仍使用简体中文。

## 会话启动必读

每次会话开始前，必须阅读以下文件：

1. `.docs/BLUEPRINT.md` — 任务蓝图与里程碑进度
2. `CLAUDE.md`（本文件）— 项目规则

## 规则

### 1. 代码签名

每个项目必须嵌入 `"Nyaa be with you."` 字符串，以非注释、运行时可见的方式存在。

- 唯一来源：`src/version.ts` 导出 `export const BLESSING = "Nyaa be with you." as const;`
- 至少 2 个运行时可见嵌入点：
  - HTML `data-blessing` 属性（`index.html` 的 `<html>` 标签）
  - 控制台启动日志（`src/main.tsx` 中 `console.log(BLESSING)`）
- 禁止：写为 `//` 注释、渲染到用户可见 UI 文本、命名为 `AUTHOR_SIGNATURE` 或 `WATERMARK`

### 2. Git 提交规范

- 使用 Conventional Commits（英文小写）：`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `style:`, `init:`, `build:`
- 禁止 `Co-Authored-By` 行
- 始终 `git add <file>` 显式添加，禁止 `git add -A` / `git add .` / `git add -u`
- 禁止：force push、`--amend` 已推送提交、`--no-verify`、`git rebase`、`git config` 修改、`reset --hard`
- 推送前：Dockerfile、docker-compose.yml、依赖锁文件、大量删除需二次确认
- 禁止提交：`.env`、`.env.*`、tokens/API keys、`node_modules/`、`dist/`、`*.log`、`.claude/settings.local.json`、>5MB 二进制文件
- 多行 commit message 使用 HEREDOC 避免 shell 引号问题

### 3. Docker 规范

- 多阶段构建：`node:20-alpine` 构建 → `nginx:alpine` 运行
- 镜像体积目标：≤ 40 MB
- 私有镜像仓库：`localhost:5000`（HTTP，无认证）
- 推送流程：`docker tag <local>:<tag> localhost:5000/<name>:<tag>` → `docker push`

### 4. 构建与重启

- 使用 `rebuild.ps1` 脚本进行 Docker 构建和重启
- 支持 `-NoCache` 参数强制无缓存构建
- 流程：build → up -d → 清理悬空镜像 → 状态报告

## Vibo Coding 工作规范

> NyaaFrame 是此规范的**发源模板**。本模板自身的维护以及所有基于此模板创建的派生项目，均须遵守本规范。派生项目的 CLAUDE.md 只需保留项目特有规则，通用工作流引用本模板即可。

### 整体流程

```
初始设计  →  设计审核  →  关键决策拍板  →  生成/更新 SSOT 计划  →  分里程碑推进  →  里程碑收尾
```

### 版本与阶段划分（V + P / 里程碑）

- **V（Version / 闭环版本）**：一个对外可用、功能闭环的版本。
- **里程碑（M）**：对应 `BLUEPRINT.md` 中的 `M0 / M1 / M2 / M3`。一个里程碑 = Vibo Coding 中的一个 P（Phase）。
- 每个里程碑必须是**可独立验证、可独立提交**的完整单元。
- 里程碑之间可以有依赖顺序，但不出现"半个里程碑交完等下个补完"的半成品状态。

### SSOT 计划（蓝图）

- 蓝图文件：`.docs/BLUEPRINT.md`，是开发阶段的**唯一事实来源**。
- 状态符号：⬜ 未开始 / 🟡 进行中 / ✅ 已完成
- 蓝图包含：里程碑任务清单、状态标记、完成日期、变更日志。
- 模板自身的蓝图使用占位符（`（根据项目需求填充）`），派生项目替换为实际任务。

### Plan 模式开发

所有里程碑的实现工作在 **plan 模式**下进行：

1. 针对当前里程碑用 `EnterPlanMode` 进入 plan 模式
2. 在 plan 中明确本里程碑的实现方案、涉及文件、验证步骤
3. 用户批准 plan 后执行实现
4. 按蓝图定义的验证步骤完成验证
5. 通过 `sync-blueprint` skill 更新 `BLUEPRINT.md`（状态符号 → ✅，添加完成日期，推进下一里程碑 → 🟡）

### 里程碑收尾（每里程碑必做）

每个里程碑完成后，**必须**执行以下收尾流程：

#### 1. 同步蓝图

- 验证所有子项实际完成
- 更新 `BLUEPRINT.md`：状态符号改为 ✅，添加 `_完成于 YYYY-MM-DD_`
- 推进下一里程碑为 🟡
- 禁止：勾选未完成项、单次提交跨多个里程碑、遗漏变更日志

#### 2. Git 提交与推送

- 通过 `commit-push` skill 完成提交和推送
- 遵循本项目的 Git 提交规范（Conventional Commits、`git add <file>`、禁止 force push 等）
- 提交前必须做 `git status` 和 secret 检查
- 蓝图更新必须与代码改动一并提交

#### 3. 里程碑交接文档

在 `.docs/` 目录下创建或更新交接文档，命名规范：`.docs/阶段交接-XXX.md`（XXX 为递增编号）。

交接文档结构：

```markdown
# NyaaFrame <版本> 阶段交接 XXX

## 交接目的
（简述本文件用途，列出续接前必读的文档）

## 当前进度
（本里程碑完成了什么，逐一列举验证通过的事项）

## 本轮已修复 / 已实现
（按文件列出本里程碑的改动要点）

## 仍需继续验证 / 已知问题
（未完成验证、已知 bug、待处理事项）

## 续接提示词
（见下方说明）
```

#### 4. 下一阶段工作交接提示词

交接文档末尾的 **"续接提示词"** 是一段**可直接粘贴给新对话 Claude Code** 的提示词，格式要求：

- 明确要求以 plan 模式推进
- 列出必读文档路径（至少含 `BLUEPRINT.md`）
- 说明当前进度（不啰嗦已完成事项的细节，只讲"到了哪里"）
- 指出下一里程碑要做的第一件事
- 重申关键约束（安全规则、不提交的文件、技术约定等）
- 长度控制在合理范围（约 10-20 行），可直接复制粘贴使用

### 跨对话接续

当在新对话中说"继续开发 NyaaFrame"或"继续开发 <派生项目>"时：

1. 读取项目的 CLAUDE.md
2. 读取 `BLUEPRINT.md`，了解全貌和当前进度
3. 读取最新的 `.docs/阶段交接-XXX.md`，获取精确的当前状态
4. 根据交接文档中的"续接提示词"确定下一步行动
5. 以 plan 模式进入下一里程碑开发

### 模板项目特注

- **维护模板自身**：按上述完整流程走，里程碑任务为实际的模板改进项。
- **基于模板创建新项目**：走完整 Vibo Coding 流程（初始设计 → 设计审核 → SSOT → 分里程碑 → 收尾）。模板初始化流程（见下节）完成后，新项目即进入正常的里程碑开发循环。
- **派生项目继承关系**：派生项目只需在自身的 CLAUDE.md 中保留特有规则（代码签名、Docker 规范等），通用工作流引用本模板规范。但为自包含起见，每个派生项目的 CLAUDE.md 末尾应有一份简版的 Vibo Coding 章节。

## 模板项目初始化流程

当基于此模板创建新项目时，按以下步骤执行：

1. 确认项目名称和开发目的
2. 确定端口（用户指定或扫描范围选择可用端口）
3. 更新 `meta.json`（项目唯一元数据来源）
4. 根据项目名重命名全局标识（package.json、docker-compose、rebuild.ps1、CLAUDE.md、version.ts）
5. 确定项目技术堆栈，拉取对应依赖
6. 更新 Docker 配置（从 meta.json 读取容器名和端口）
7. 根据实际需求修改 `rebuild.ps1` 脚本
8. 确定 GitHub 仓库地址（从 meta.json 读取）
9. 修改 LICENSE 文件签名和地址（从 meta.json 读取）
10. 重新生成 README
11. 更新 `src/version.ts` 的 `APP_NAME`
12. 建立 `.ref/` 目录（已被 .gitignore 排除版本管理）
13. 清理初始化模板流程和 Claude Code 备忘
14. 初始化 GitHub 仓库并进行首次推送
15. 通知开始进行开发 —— 此时进入 Vibo Coding 规范中的"初始设计 → 设计审核 → SSOT 计划"流程

### meta.json 说明

`meta.json` 是项目的标准化元数据文件，记录项目名称和特征信息。初始化流程中所有需要项目名称、地址、端口等信息的步骤均从此文件读取，确保单一来源、全局一致。
