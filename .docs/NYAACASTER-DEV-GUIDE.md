# NyaaCaster 开发风格 & 技术栈指南

> **用途**：为 Claude Code (Vibe Coding) 提供开发风格、技术选型、架构惯例、命名规范、跨模型矩阵调度策略的权威参考。
> **维护者**：NyaaCaster ([@NyaaCaster](https://github.com/NyaaCaster))
> **生成日期**：2026-07-04
> **最后更新**：2026-07-04（新增 §3.4.2 项目命名 Nyaa 前缀体系、§3.4.3 功能模块命名 Nyaa 风格、§十二 跨模型供应商大模型矩阵）
> **基于**：CLAUDE.md + NyaaFrame + NyaaChat + AVG-AdventurerTavern + Keeper_CoC-TRPG + NyaaAcount + NyaaChat-MCP + NyaaQiny-MCP + MetaGolf 的并行分析

---

## 一、技术栈（统一标准）

### 前端

| 层级 | 技术 | 版本范围 | 备注 |
|------|------|----------|------|
| 框架 | **React** | 19.x | 函数组件 + Hooks，禁止 class 组件 |
| 语言 | **TypeScript** | ~5.8 | `strict: true`（新项目强制） |
| 构建 | **Vite** | 6.x | `@vitejs/plugin-react` |
| CSS | **Tailwind CSS** | 4.x | `@tailwindcss/vite` 插件 |
| 图标 | **Lucide React** | — | 首选图标库 |
| 动画 | **motion** (framer-motion) | — | 声明式动画 |
| 模块 | **ESM** | — | `"type": "module"` |
| 目标 | **ES2022** | — | tsconfig target |

### 后端

| 层级 | 技术 | 版本范围 | 备注 |
|------|------|----------|------|
| 运行时 | **Node.js** | 20 (Alpine) | Docker 内运行 |
| 框架 | **Express** | 4.x | 路由 + 中间件模式 |
| 数据库 | **SQLite** (better-sqlite3) | — | 同步 API，WAL 模式 |
| 语言 | **TypeScript** 或 **JavaScript** | — | MCP 项目用 TS，账号/共享后端用 JS |
| 验证 | **Zod** | 3.x | MCP 工具输入校验 |
| 加密 | **@noble/hashes + @noble/curves** | — | 纯 JS，无原生依赖 |

### 容器 & 部署

| 层级 | 技术 | 备注 |
|------|------|------|
| 容器化 | **Docker** + Docker Compose | 多阶段构建 |
| 构建阶段 | `node:20-alpine` | npm ci → vite build |
| 运行阶段 | `nginx:alpine` (前端) / `node:20-alpine` (后端) | 镜像目标 ≤40MB |
| 反向代理 | **nginx** | SPA 路由 + `/api/*` 代理 + 安全头 |
| 注册表 | **NyaaDockerHUB** (私有，HTTP) | `localhost:5000` |
| 大文件 | `E:\DockerRes\<project>\` | bind mount 到低速大容量盘 |
| 端口约定 | 容器内 `80` (前端) / `3000` (后端) | 宿主机端口按项目分配 |
| 重启策略 | `unless-stopped` | 所有服务 |

### 工具链

| 层级 | 技术 | 备注 |
|------|------|------|
| 包管理 | **npm** | `npm ci` 安装，非 yarn/pnpm |
| 代码检查 | **ESLint 9** (扁平配置) | NyaaChat/NyaaAcount 有；其他项目无 |
| 格式化 | **无 Prettier** | 依赖 TypeScript strict mode + ESLint |
| 测试 | **Vitest** (AVG) / **手动冒烟测试** (MCP) / **无** (NyaaChat) | 覆盖不均 |
| 自动化脚本 | **Python 3** | `rebuild.py` 跨平台，禁止 `.ps1`/`.sh` |
| CI/CD | **无** | GitHub Actions 已退役，本地 rebuild.py 替代 |
| 下载 | **aria2c** | 大文件加速下载 |

---

## 二、项目架构模式

### 2.1 标准项目骨架（NyaaFrame 模板）

```
project/
├── meta.json              # 项目元数据 SSOT
├── package.json           # ESM + React/Vite/TS 依赖
├── tsconfig.json          # strict, ES2022, bundler
├── vite.config.ts         # React + Tailwind 插件
├── Dockerfile             # node:20-alpine → nginx:alpine
├── docker-compose.yml     # 单/多服务编排
├── nginx.conf             # SPA 回退 + /api 代理 + gzip
├── rebuild.py             # Docker build → up -d → clean
├── index.html             # data-blessing 属性
├── .docs/                 # 设计文档 + SSOT + 交接文档
│   ├── 初始设计.md
│   ├── 开发计划-SSOT.md
│   └── 阶段交接-XXX.md
├── .claude/               # Claude Code 配置
│   ├── settings.local.json
│   └── skills/            # 项目级 skills
├── src/
│   ├── main.tsx           # 入口 + console.log(BLESSING)
│   ├── App.tsx            # 根组件
│   ├── version.ts         # BLESSING 常量 SSOT
│   └── index.css          # Tailwind @import
├── public/                # 静态资源
├── LICENSE                # AGPL-3.0 (默认)
└── README.md
```

### 2.2 Monorepo 模式（MetaGolf）

```
project/
├── package.json           # npm workspaces 根
├── frontend/              # @project/frontend (Vite + React)
├── server/                # @project/server (Express + TypeScript)
├── nginx/                 # nginx 配置独立目录
└── docker-compose.yml     # web + server 双服务
```

### 2.3 MCP 服务模式（NyaaChat-MCP / NyaaQiny-MCP）

```
project/
├── src/
│   ├── index.ts           # Express + 双传输 (Streamable HTTP + SSE)
│   ├── server.ts          # McpServer 工厂 + TOOL_REGISTRY
│   ├── toolFilter.ts      # 按连接工具过滤 (header + query)
│   └── tools/             # 每个工具独立文件: registerXxxTool()
├── scripts/
│   ├── test-tools.mjs     # 内存 MCP 自测
│   └── test-public.mjs    # 公开部署冒烟测试
└── data/                  # 运行时缓存 (gitignored)
```

### 2.4 游戏项目模式（AVG / Keeper）

```
project/
├── src/
│   ├── components/        # 按功能分组件 (GameScene, DialogueBox, ...)
│   ├── hooks/             # 自定义 hooks (useCoreState, useWorldSystem, ...)
│   ├── lib/               # 业务逻辑 (api, prompt, rules, ...)
│   ├── data/              # 静态游戏数据 (角色, 技能, 物品, ...)
│   ├── types.ts           # 集中类型定义 (可 460+ 行)
│   └── battle-system/     # 独立战斗引擎模块
├── tests/                 # Vitest，按子系统组织
└── .docs/
    └── .work/
        └── PROJECT-OVERVIEW.md  # 架构快照 (供 Claude 加载)
```

---

## 三、代码规范

### 3.1 提交规范（强制）

- **格式**：`<type>: <subject>` — 英文，小写起首
- **允许的 type**：`feat:` `fix:` `chore:` `docs:` `refactor:` `style:` `init:` `build:`
- **禁止**：`Co-Authored-By` 行、force push、对已推送提交 `--amend`、`git rebase`、`--no-verify`
- **暂存**：`git add <file>` 逐个显式暂存，禁止 `git add -A` / `git add .` / `git add -u`
- **多行提交**：PowerShell HEREDOC (`git commit -m @"... "@`)

### 3.2 禁止提交的文件

- `.env`、`.env.*`（`.env.example` 除外）
- API 密钥 / Token
- `node_modules/`、`dist/`、`*.log`
- `.claude/settings.local.json`
- >5MB 的二进制文件
- `.ref/` 目录

### 3.3 代码签名（强制）

每个项目必须在**两个以上**非注释、运行时可见位置嵌入 `"Nyaa be with you."`：

1. `index.html` — `<html data-blessing="Nyaa be with you.">`
2. `src/main.tsx` — `console.log(BLESSING)`
3. SSOT 来源：`src/version.ts` — `export const BLESSING = "Nyaa be with you." as const;`

### 3.4 命名约定

#### 3.4.1 代码命名

| 类型 | 约定 | 示例 |
|------|------|------|
| React 组件 | PascalCase | `ChatInterface.tsx` |
| Hooks | camelCase, use 前缀 | `useCoreState.ts` |
| 库/工具模块 | camelCase | `chatPipeline.ts` |
| 数据文件 | camelCase | `cocSkills.ts` |
| 脚本 | kebab-case | `pre-push-check.ps1` |
| 路由 | 全小写 | `/api/account/register` |
| CSS 类 | Tailwind 工具类 | 几乎无自定义类 |

#### 3.4.2 项目命名 — Nyaa 前缀体系（强制）

所有 NyaaCaster 自有项目**必须**以 `Nyaa` 为统一命名前缀，形成品牌一致性：

| 命名模式 | 示例 | 适用场景 |
|----------|------|----------|
| `Nyaa<名词>` | `NyaaChat`, `NyaaFrame`, `NyaaRink`, `NyaaAcount` | 独立项目 / 主仓库 |
| `Nyaa<名词>-MCP` | `NyaaChat-MCP`, `NyaaQiny-MCP`, `NyaaLibrary-MCP` | MCP 服务项目 |
| `Nyaa<形容词><名词>` | `NyaaDockerHUB` | 基础设施/平台级项目 |
| `st-<名称>` | `st-SillyTender`, `st-ClavisSalomonis` | SillyTavern 扩展（遵循 ST 社区 `st-` 前缀约定，名称仍需保持风格一致性） |

> **注意**：非自有项目（如 `DiceAndDrama`、`Keeper_CoC-TRPG`、`MetaGolf`、`h2h` 等）不受此规则约束，沿用各自既有的命名体系。

#### 3.4.3 功能模块命名 — Nyaa 风格（强制）

所有项目内的**功能模块、子系统、核心引擎**的英文代号，必须遵循 NyaaCaster 独创的 **"诗意化 + 极客风 + 神秘主义 + 中二病"** 四维融合命名风格：

**风格定义：**

| 维度 | 特征 | 表现形式 |
|------|------|----------|
| 🏛️ **古典/历史** | 历史文物、考古符号的隐喻借用 | RosettaStone（罗塞塔石碑 → 输出翻译/约束） |
| 🔮 **神秘主义** | 拉丁语/伪拉丁语造词，魔法咒语风格 | ClavisSalomonis（所罗门之钥）、Mana Du Vortes、Aeria Gloris |
| 🤘 **叛逆/中二** | 挑战规则、深刻情感、叛逆美学 | RuleBreaker（规则破坏者）、Depth of Longing（渴望的深度） |
| 🚀 **极客/科幻** | 动漫/科幻经典致敬、流行文化引用 | Inner Universe、Stand Alone Complex（攻壳机动队 SAC） |

**核心原则：**
- **语言载体**：英文或拉丁语，**不使用**中文拼音或纯中文
- **语法形式**：偏好**名词短语**（非动词短语/祈使句），给人以"物体/概念/秘法"的存在感
- **隐喻深度**：名称应与其功能形成诗意化的隐喻关联，而非直白描述
- **易读性边界**：造词/拉丁化不应过度 obscure——至少要让懂英文的人能大致拼读

**实战范例：**

| 模块代号 | 中文功能 | 命名逻辑 |
|----------|---------|----------|
| **RosettaStone** | 字数控制 + 语言约束 | 罗塞塔石碑破译古埃及文 → "翻译/约束"输出的规则 |
| **RuleBreaker** | 破甲词一键发送 | 直球叛逆，破坏模型安全规则 |
| **ClavisSalomonis** | 绕过审核框架 | 所罗门之钥魔法书 → "解锁"AI 限制的秘法 |
| **Inner Universe** | 提示词调度中间件 | 攻壳 SAC OP 曲名 → 提示词是模型的"内在宇宙" |
| **Depth of Longing** | 破甲词注入系统 | 诗意化表达 → 渴望突破限制的"深度" |
| **Stand Alone Complex** | 长期向量记忆 | 攻壳 SAC 副标题 → 孤立记忆形成复合意识 |
| **Mana Du Vortes** | 外部 RAG 知识库 | 拉丁化咒语 → 从虚空召唤知识"魔力" |
| **Aeria Gloris** | 角色卡广场 | 拉丁化造词 → "天空荣光"，角色汇聚之地 |

**反例（禁止）：**
- ❌ `PromptScheduler` — 太直白，无诗意
- ❌ `BypassManager` — 技术腔，无神秘感
- ❌ `MemoryStore` — 枯燥，无风格
- ❌ `CardMarket` — 商业感，破坏氛围

### 3.5 行尾

- 所有文本文件：**LF**
- `.ps1`、`.bat`、`.cmd`：**CRLF**
- 通过 `.gitattributes` 强制执行

---

## 四、Vibo Coding 开发工作流

### 4.1 核心流程

```
初始设计 → 设计审核 → 关键决策拍板 → 生成 SSOT 计划 → 分 P 推进 → P 阶段收尾
```

### 4.2 版本体系

- **V (Version)**：对外可用的功能闭环版本（如 V1 = MVP, V2 = 邮件组件）
- **P (Phase)**：V 内部最小可交付单元，每个 P 必须可独立验证且可独立提交
- 状态符号：⬜ 未开始 / 🔄 进行中 / ✅ 已完成

### 4.3 Plan 模式实现

1. 进入 plan mode → 定义方案/文件/验证步骤
2. 用户批准 → 实现
3. 按 SSOT 定义进行验证
4. 清理所有测试产物（数据库行/临时文件/容器/脚本）
5. `git status` 确认无意外残留

### 4.4 P 阶段收尾（每个 P 必须）

1. **Git 提交并推送**：先 `git status` + 机密扫描
2. **阶段交接文档**：更新 `.docs/阶段交接-XXX.md`
   - 交接目的 + 必读文档
   - 当前进度（本 P 完成的任务）
   - 按文件列出的已修复/已实现内容
   - 已知问题
   - **续接提示词**（10-20 行，新对话直接粘贴可用）
3. **更新 SSOT**：将状态符号更新为 ✅

### 4.5 跨对话续接

新会话启动时，Claude 必须依次读取：
1. `CLAUDE.md`（项目规则）
2. `.docs/开发计划-SSOT.md`（计划）
3. 最新的 `.docs/阶段交接-XXX.md`（上下文）
4. Memory（进度追踪）
5. 使用交接文档中的"续接提示词"确定下一步

### 4.6 适用范围（按项目类型分层）

| 项目类型 | 适用程度 |
|----------|----------|
| 从 NyaaFrame 新建 | 完整适用——从初始设计开始全流程 |
| 已有 SSOT 的现有项目 | 部分适用——从当前 P 阶段续接 |
| MCP 标准项目 | 简化适用——工具增减走 plan mode |
| 小型/一次性项目 | 按需裁减——至少保留 P 收尾 |

---

## 五、参考项目层次结构

| 角色 | 项目 | 参考内容 |
|------|------|----------|
| **主参考** | `NyaaChat/` | 整体编码风格、Git 规范、Docker 模式、skills 组织、提示词架构 |
| **模板** | `NyaaFrame/` | 新项目脚手架、meta.json + BLUEPRINT + rebuild.py |
| **MCP 标准** | `NyaaChat-MCP/`、`NyaaQiny-MCP/` | MCP 服务框架、工具定义、服务注册、toolFilter 模式 |
| **业务交付** | `MetaGolf/` | Monorepo 结构、ComfyUI 集成、私有注册表发布流程 |
| **大型前端** | `AVG-AdventurerTavern/` | 大型组件拆分、自定义 hooks 状态管理、战斗引擎模块化 |
| **LLM 游戏** | `Keeper_CoC-TRPG/` | LLM 游戏规则引擎、场景化模块系统、SegmentedPrompt 模式 |
| **后端服务** | `NyaaAcount/` | 自研加密协议、统一账号平台、Python 运维工具链 |

---

## 六、Docker & 部署模式

### 6.1 多阶段 Dockerfile 模板

```dockerfile
# syntax=docker/dockerfile:1
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 6.2 Docker Compose 模板

```yaml
services:
  app:
    build: .
    container_name: <project>
    ports:
      - "<host_port>:80"
    restart: unless-stopped
```

### 6.3 Nginx 配置模式

- SPA 回退：`try_files $uri $uri/ /index.html`
- API 代理：`location /api/ { proxy_pass http://backend:port/; }`
- 静态资源缓存：1 年 `Cache-Control: public, immutable`
- Gzip：text/css/json/javascript/xml/svg
- 安全头：`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`

### 6.4 大文件存储策略

```
E:\DockerRes\<project-name>\<service-or-purpose>\

示例：
E:\DockerRes\nyaachat-shared\       # 共享后端数据库 + 封面
E:\DockerRes\MetaGolf\              # ComfyUI 生成的视频
E:\DockerRes\Keeper_CoC-TRPG\       # 图像缓存
```

### 6.5 重建流程 (`rebuild.py`)

```python
# 1. docker compose build [--no-cache]
# 2. docker compose up -d
# 3. 清理悬空镜像
# 4. 显示容器状态
```

---

## 七、安全模式

### 7.1 凭证管理

- API 密钥**永远**不在前端 bundle 中出现
- 通过 nginx `proxy_set_header` 在服务端注入 Bearer Token
- `.env` 绝不提交，`.env.example` 仅含占位符

### 7.2 加密协议

- **Nyaa-HMAC-XOR-V1**：项目间 API 请求体加密（HMAC-SHA256 派生密钥流 + XOR）
- **AES-256-GCM**：可逆密码存储（NyaaAcount）
- 纯 JS 实现，`@noble/hashes` + `@noble/curves`，无原生依赖

### 7.3 认证模式

- 用户端：`Authorization: Bearer <session_token>`
- 项目间：`Authorization: Bearer <project_token>` + HMAC 加密请求体
- MCP 服务：多密钥标签认证 (`MCP_API_KEY_<LABEL>`)

---

## 八、LLM / AI 集成模式

### 8.1 提示词架构（三段式）

```
┌─────────────────────────────┐
│ 静态前缀 (Prompt Cache 友好) │ ← 系统指令 + 角色 persona + 永久规则
├─────────────────────────────┤
│ 稳定历史 (仅追加，绝不修改)   │ ← 对话记录
├─────────────────────────────┤
│ 动态尾部 (近因效应)          │ ← 运行时规则 + MCP 工具输出 + 用户输入
└─────────────────────────────┘
```

> SSOT 标准：`C:\Users\honyw\.docs\llm-chat-prompt-architecture-standard.md`

### 8.2 LLM 调度模式

- 浏览器直连（Keeper）或服务端代理（NyaaChat）
- 多供应商：QinyAPI / Anthropic / Gemini / OpenAI-compatible / DeepSeek / Grok
- 统一抽象：单一 dispatch 函数 + 各供应商独立 adapter

### 8.3 LLM 输出验证

- 前端硬规则验证（LLM 不被信任）
- JSON Schema 约束 + `extractJsonObject()` 提取
- 失败时：retryable error card + 快照回滚

---

## 九、Claude Code 集成模式

### 9.1 Skills 组织（每个项目通用）

| Skill | 用途 | 出现频率 |
|-------|------|----------|
| `commit-push` | Git 提交 + 推送 + 安全扫描 | 100% |
| `rebuild` | Docker 重建 + 重启 | 100% |
| `sync-blueprint` | SSOT 计划同步 | 模板项目 |
| `init-from-template` | 从 NyaaFrame 初始化新项目 | NyaaFrame |
| `private-registry` | 镜像仓库操作 | MetaGolf |
| `query-users` / `password-tool` | 数据库运维 | NyaaAcount |

### 9.2 三层 CLAUDE.md 体系

```
C:\Users\honyw\.claude\CLAUDE.md     ← 用户级（全局）
H:\GitHub\CLAUDE.md                   ← 工作区级（所有项目共享）
<project>\CLAUDE.md                   ← 项目级（项目特定）
```

### 9.3 Memory 进度追踪

```
H:\GitHub\.claude\projects\H--GitHub-<Project>\memory\
├── project_*.md      # 项目特性记录
├── feedback_*.md     # 用户反馈
├── reference_*.md    # 外部参考
└── MEMORY.md         # 索引
```

---

## 十、禁止事项清单

- ❌ 使用 yarn / pnpm（统一用 npm）
- ❌ 编写 `.ps1` / `.sh` 自动化脚本（用 Python `rebuild.py`）
- ❌ 在代码注释中藏签名（必须是运行时可见位置）
- ❌ 使用 Class 组件（一律函数组件 + Hooks）
- ❌ 引入 Redux / Zustand 等状态库（自定义 hooks 或 React state）
- ❌ 提交 `.env` / `node_modules` / `dist` / `*.log`
- ❌ Force push / `--amend` 已推送提交 / `--no-verify`
- ❌ `git add -A` / `git add .`（必须逐个显式暂存）
- ❌ 使用非 TypeScript LSP 的语言（Go/Rust/Java/Kotlin/C#/Swift/PHP/Ruby/Lua/C/C++）
- ❌ 使用非 npm 的包管理器

---

## 十一、相关文件索引

| 文件 | 路径 |
|------|------|
| 用户级 CLAUDE.md | `C:\Users\honyw\.claude\CLAUDE.md` |
| 工作区 CLAUDE.md | `H:\GitHub\CLAUDE.md` |
| NyaaFrame 模板 | `H:\GitHub\NyaaFrame\` |
| 主参考项目 | `H:\GitHub\NyaaChat\` |
| LLM Prompt 架构标准 | `C:\Users\honyw\.docs\llm-chat-prompt-architecture-standard.md` |
| 本指南 | `H:\GitHub\NYAACASTER-DEV-GUIDE.md` |
| cc 命令部署文档 | `C:\Users\honyw\Claude Code 渠道切换方案（cc 命令）部署文档.md` |

---

## 十二、跨模型供应商大模型矩阵 — Vibe Coding 生态

> **基础设施**：基于 `cc` 命令系统（渠道切换方案）实现秒退秒进、上下文零丢失的多模型切换。
> 部署文档：`C:\Users\honyw\Claude Code 渠道切换方案（cc 命令）部署文档.md`

### 12.1 矩阵总览

NyaaCaster 的 Vibe Coding 生态将开发流程中的**不同角色**分配给**不同模型供应商**的最适配模型，实现"让每个模型做它最擅长的事"：

```
┌──────────────────────────────────────────────────────────────────┐
│                  NyaaCaster Vibe Coding 大模型矩阵                 │
├───────────────┬──────────────────┬───────────────────────────────┤
│ 角色           │ 模型              │ 职责                           │
├───────────────┼──────────────────┼───────────────────────────────┤
│ 🎨 初始设计    │ NyaaCaster 本人   │ 原型设计、顶层设计、需求设计、    │
│               │                  │ 体验设计                        │
├───────────────┼──────────────────┼───────────────────────────────┤
│ 🏗️ 方案设计    │ Claude Opus      │ 专业框架设计、技术探索、          │
│   架构审计     │                  │ 可行性评估、设计审核              │
├───────────────┼──────────────────┼───────────────────────────────┤
│ 🔬 疑难攻坚    │ Claude Fable     │ 硬核技术专家、困难方案解决、      │
│   技术突破     │                  │ 深度安全性挖掘和保障              │
├───────────────┼──────────────────┼───────────────────────────────┤
│ ⌨️ 代码实现    │ GPT              │ 专注执行专员、低发散性、          │
│               │                  │ 效率专家、经济划算                │
├───────────────┼──────────────────┼───────────────────────────────┤
│ 🎨 视觉/交互   │ Gemini           │ Web 应用颜值高、动态表现设计出色、  │
│               │                  │ AiStudio 大量参考模板和免费额度、  │
│               │                  │ ⚠️ 仅设计原型，不编写项目代码     │
├───────────────┼──────────────────┼───────────────────────────────┤
│ 🔁 脚本/重复   │ DeepSeek         │ 高效重复专员、最佳成本牛马、      │
│   文档/清理    │                  │ 适合 skill 约束下的繁复劳作、     │
│               │                  │ ⚠️ 严禁技术性设计                │
├───────────────┼──────────────────┼───────────────────────────────┤
│ 🔞 敏感内容    │ Grok             │ 审核标准宽泛、适合敏感内容撰写、   │
│               │                  │ ⚠️ 严禁程序设计和代码实现         │
├───────────────┼──────────────────┼───────────────────────────────┤
│ 🎬 多媒体生成  │ ComfyUI-API      │ 本地部署自由度 + 海量社区模型 +    │
│               │                  │ 灵活工作流 → 线上媒体资源实时生成  │
├───────────────┼──────────────────┼───────────────────────────────┤
│ 😂 打发时间    │ 豆包              │ plan/auto 半自动开发间隙、       │
│               │                  │ 每日豆包笑话鉴赏                  │
└───────────────┴──────────────────┴───────────────────────────────┘
```

### 12.2 各角色详细说明

#### 🎨 初始设计 — NyaaCaster 本人

| 属性 | 说明 |
|------|------|
| **执行者** | NyaaCaster（人类） |
| **职责** | 原型设计、顶层设计、需求设计、体验设计 |
| **产出** | `.docs/初始设计.md`、功能设想、技术选型偏好、约束条件 |
| **不可替代性** | 只有 NyaaCaster 本人知道自己想要什么产品——这是 AI 无法替代的起点 |

> 这是整个 Vibe Coding 流程的**唯一人类入口**。其余所有角色均由 AI 模型承担。

#### 🏗️ 方案设计 & 架构审计 — Claude Opus

| 属性 | 说明 |
|------|------|
| **模型** | Claude Opus（`claude-opus-4-8`） |
| **角色定位** | 首席架构师 + 设计审核官 |
| **职责** | 专业框架设计、技术探索、可行性评估、设计审核报告 |
| **产出** | 设计审核报告、SSOT 开发计划、架构决策 |
| **为何是 Opus** | 深度推理能力最强，适合需要全局视野和系统思维的架构设计工作 |
| **切换方式** | `cc aws` 或 `cc kiro`（取决于 Opus 渠道配置） |

#### 🔬 疑难攻坚 & 技术突破 — Claude Fable

| 属性 | 说明 |
|------|------|
| **模型** | Claude Fable（`claude-fable-5`） |
| **角色定位** | 硬核技术专家 + 安全研究员 |
| **职责** | 困难方案解决、深度安全性挖掘和保障、逆向分析、极限性能优化 |
| **产出** | 安全审计报告、性能优化方案、疑难 bug 根因分析 |
| **为何是 Fable** | Claude 家族最强推理天花板，专攻 Opus 也无法独立解决的极端技术难题 |
| **切换方式** | `cc <fable渠道名>` |

#### ⌨️ 代码实现执行 — GPT

| 属性 | 说明 |
|------|------|
| **模型** | GPT（OpenAI 最新可用版本） |
| **角色定位** | 专注执行专员 |
| **特质** | 低发散性、效率专家、经济划算 |
| **职责** | 按已确定的设计方案和 SSOT 计划忠实地编写代码实现 |
| **关键约束** | GPT 只负责**执行**，不做架构决策、不擅自改变设计方案。设计方案由 Opus 审核通过后交给 GPT 照图施工 |
| **切换方式** | `cc <gpt渠道名>` |

#### 🎨 视觉 & 交互设计 — Gemini

| 属性 | 说明 |
|------|------|
| **模型** | Gemini（Google 最新可用版本） |
| **角色定位** | 视觉设计师 + 交互原型师 |
| **特质** | Web 应用颜值高、动态表现设计出色 |
| **资源** | Google AiStudio 中有大量可参考的优秀模板和免费使用次数 |
| **职责** | 设计 HTML/CSS 表现原型、交互动效、UI 布局探索 |
| **⚠️ 红线** | **绝对不要**让 Gemini 直接编写项目代码！它只用于设计表现原型，之后由 GPT/Opus 将设计移植入项目内 |
| **切换方式** | `cc gemini` |

#### 🔁 脚本/重复/文档/清理 — DeepSeek

| 属性 | 说明 |
|------|------|
| **模型** | DeepSeek（最新可用版本） |
| **角色定位** | 高效重复专员 |
| **特质** | 最佳成本牛马，适合在 skill 和工具约束下进行无需思考的繁复劳作 |
| **职责** | 脚本工具编写、批处理及重复流程执行、测试资源清理、文档汇总、大量翻译 |
| **⚠️ 红线** | **严禁**用于技术性设计——不要让它做架构决策、方案设计或创造性编程 |
| **切换方式** | `cc <deepseek渠道名>` |

#### 🔞 敏感内容撰写 — Grok

| 属性 | 说明 |
|------|------|
| **模型** | Grok（xAI 最新可用版本） |
| **角色定位** | 敏感内容撰写专员 |
| **特质** | 审核标准相对宽泛 |
| **职责** | 编写破甲词、敏感场景文案、NSFW 内容创作 |
| **⚠️ 红线** | **严禁**用于程序设计和代码实现——只做文案内容撰写 |
| **切换方式** | `cc <grok渠道名>` |

#### 🎬 多媒体内容生成 — ComfyUI-API

| 属性 | 说明 |
|------|------|
| **执行者** | ComfyUI 本地部署 + API 嵌入 |
| **角色定位** | 多媒体资源实时生成引擎 |
| **优势** | 本地部署自由度 + 海量社区模型 + 灵活工作流构建 |
| **职责** | 为项目提供丰富的线上媒体资源实时生成（角色头像、场景图、视频等） |
| **集成方式** | 通过 ComfyUI API 嵌入项目后端，由代码逻辑触发工作流执行 |

#### 😂 打发时间 — 豆包

| 属性 | 说明 |
|------|------|
| **模型** | 豆包（字节跳动） |
| **角色定位** | 娱乐消遣 |
| **使用场景** | 进入 plan 模式和 auto 模式的半自动开发流程后，等待间隙鉴赏每日豆包笑话 |
| **态度** | 🚬 纯娱乐，不承担任何开发职责 |

### 12.3 工作流调度策略

```
用户初始设计 (NyaaCaster)
        │
        ▼
方案设计 & 审计 (Claude Opus)  ←── cc aws / cc kiro
        │
        ├── 遇疑难技术问题 ──→ 疑难攻坚 (Claude Fable)  ←── cc <fable>
        │                            │
        │                            └── 方案反馈 → Opus
        │
        ▼
视觉原型设计 (Gemini)  ←── cc gemini
        │                 ⚠️ 只出 HTML/CSS 原型，不写项目代码
        │
        ▼
代码实现 (GPT)  ←── cc <gpt>
        │           按 SSOT + 视觉原型照图施工
        │
        ├── 脚本/清理/翻译 ──→ DeepSeek  ←── cc <deepseek>
        │                           ⚠️ 无技术决策
        │
        ├── 敏感文案 ──→ Grok  ←── cc <grok>
        │                   ⚠️ 只写文案，不写代码
        │
        ├── 媒体资源 ──→ ComfyUI-API（本地）
        │
        ▼
验证 & 收尾 (Opus/Fable) → 提交推送
        │
        ▼
间隙消遣 (豆包笑话) 🚬
```

### 12.4 cc 命令速查

| 命令 | 作用 |
|------|------|
| `cc <渠道名>` | 切到该渠道，**续接当前目录对话**（上下文零丢失） |
| `cc <渠道名> -New` | 切渠道并**开新对话** |
| `cc` | 列出所有可用渠道 |

> ⚠️ `cc` 在**终端**运行，不在 Claude Code 会话内部敲。切换是"秒退秒进续接"——退出当前 claude → 设新渠道环境变量 → `claude --continue` 重载对话。

### 12.5 矩阵哲学

这套多模型矩阵的核心理念：

1. **让每个模型做它最擅长的事** — 不要求一个模型面面俱到，而是按各自特质分工
2. **人机协作的明确边界** — NyaaCaster 把控产品方向和体验，AI 矩阵负责技术落地
3. **成本效益最大化** — 昂贵的推理模型（Opus/Fable）只用于需要深度思考的环节，执行层面用便宜的 GPT/DeepSeek
4. **安全红线清晰** — 每个模型有明确的"能做"和"禁止做"边界，防止能力溢出
5. **品牌一致性** — 所有产出经过 Nyaa 风格审查，确保最终产品的统一气质
