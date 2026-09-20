# 欧加真全版本内核快速构建（5.10 / 5.15 / 6.1 / 6.6 / 6.12）

OPPO/一加/真我 GKI 内核自动化编译（照 cctv18 三仓的 fastbuild 模式），**5.10-6.12 全版本合并到一个仓**。

## 支持的内核版本

### 5.10.x（android12-5.10，KMI gen 9）

| x | 平台 | 覆盖机型 |
|---|---|---|
| 5.10.66 | mt6895 / sm8450 | 一加10R、Ace Race、一加10Pro |
| 5.10.110 | mt6895 / mt6983 | Ace Racing、Ace 2V |
| 5.10.149 | mt6895 / mt6983 | Ace、Ace Racing、一加平板、Nord 3 |
| 5.10.168 | mt6895 / mt6983 | 10R、Ace、Ace Race、Ace 2V |
| 5.10.198 | mt6983 | Nord 3 5G |
| 5.10.209 | mt6895 / mt6983 / sm8450 / sm8475 | 10R、一加平板、一加10Pro、一加11R、Ace Pro |
| 5.10.226 | mt6983 / sm8450 / sm8475 | Ace 2V、Nord 3、一加平板、一加10Pro、Ace 2、Ace Pro、一加11R |
| 5.10.236 | mt6895 / mt6983 / sm8450 / sm8475 | Ace、Ace Race、Ace 2V、Nord 3、一加平板、一加10Pro、Ace 2、一加11R、一加10T |

### 5.15.x（android13-5.15，KMI gen 8）

| x | 平台 | 覆盖机型 |
|---|---|---|
| 5.15.74 | sm8550 | 一加11（ColorOS 13.1） |
| 5.15.123 | sm8550 | 一加11（ColorOS 14） |
| 5.15.167 | sm8550 | 一加11、Ace 2 Pro、Ace 3、一加12R、OnePlus Open（ColorOS 15） |
| 5.15.180 | sm8550 / sm7550 / mt6985 | 一加11、Ace 2 Pro、Ace 3、一加12R、Open、Nord CE4、Find X6、Find N3 Flip（ColorOS 16） |

### 6.1.x（android14-6.1）— 合并自 sm8650 仓

| x | 覆盖机型 |
|---|---|
| 6.1.57 / 6.1.75 / 6.1.115 / 6.1.118 / 6.1.128 / 6.1.134 / 6.1.141 / 6.1.157 | 一加12、Ace 3、Ace 3 Pro、Ace 5、Nord 4 等 sm8650 平台（含天玑特供变体） |

### 6.6.x（android15-6.6）— 合并自 sm8750 仓

| x | 覆盖机型 |
|---|---|
| 6.6.30 / 6.6.50 / 6.6.56 / 6.6.57 / 6.6.66 / 6.6.89 / 6.6.118 | 一加13、Ace 5 Pro、Find X8 等 sm8750 平台（`_mtk` 后缀 = 天玑特供变体） |

### 6.12.x（android16-6.12）— 合并自 sm8850 仓

| x | 覆盖机型 |
|---|---|
| 6.12.23 / 6.12.38 / 6.12.58 | 一加15、Ace 6、Find X9 等 sm8850 平台（`_mtk`/`_gki` 后缀 = 天玑/GKI 变体） |

## 上游来源与同步

**每个子版本的源码来源、上游更新怎么查、怎么同步 → 见 [`docs/上游与同步.md`](docs/上游与同步.md)**（权威文档，任何接手的人/AI 先读它）。

速览：5.x 源码来自 OnePlusOSS 官方仓；6.x 来自 cctv18 三仓（sm8650/sm8750/sm8850）的预修版；SUSFS/KPN 等外部依赖动态拉取。

## 编译方式

- **入口**：Actions 列表只有 5 个线级入口「内核构建 - Linux 5.10/5.15/6.1/6.6/6.12」，一键构建该线全部子版本；`only_sub_level` 填版本号（如 226）可只建单个。每个子版本独立出 AK3 包、独立 Release。
- **模块位置（重要）**：35 个单版本构建文件是 `workflow_call` 可复用模块，放在 **`modules` 分支**的 `.github/workflows/`（放在默认分支会占据 Actions 列表）。线级入口通过 `uses: BailinT/oppo_oplus_realme_all/.github/workflows/<file>.yml@modules` 跨分支调用。
- **改动模块的流程**：切到 `modules` 分支改 → push → 线级入口立即生效（无需重建 main）。改完先在一条线跑 `only_sub_level=<单版本>` 验证。
- 源码：OnePlusOSS 官方 common 仓 + cctv18 三仓（6.x 用 cctv18 预修版）
- 死链修复：官方 common 仓的 `drivers/soc/oplus/storage` 等是指向未开源 vendor 的死链，workflow 内自动替换
- SUSFS：ShirkNeko/susfs4ksu（5.x）/ cctv18/susfs4oki（6.x）
- 工具链：Clang 20（5.10/5.15/6.1）、Clang 18（6.6）、Clang 19（6.12）
- 产物：AK3 包（AnyKernel3）

## 资源目录结构（版本化）

```
lib/                      # 公共（ccache / fakestat）
other_patch/              # 按版本命名（cve-*-6.1.patch / 6.6 / 6.12 共存）
droidspaces_patch/        # 按版本命名共存；6.12/ 子目录放 6.12 专属 evdi
zram_patch/
  ├── 001-lz4.patch ...   # 6.1 套（5.10/5.15/6.1 共用，与 sm8650 字节一致）
  ├── 6.6/                # 6.6 套
  └── 6.12/               # 6.12 套 + zram.zip
zram.zip                  # 6.1/6.6 共用（字节相同）
```

## 状态

- [x] 5.10 全 8 个 x — ✅ 12/12 绿（含 LTO/CFI 修复）
- [x] 5.15 全 4 个 x — ✅ 全绿
- [x] 6.1 全 8 个 x — 合并入库（源自 sm8650 仓，已验证）
- [x] 6.6 全 9 个 x — 合并入库（源自 sm8750 仓，已验证）
- [x] 6.12 全 6 个 x — 合并入库（源自 sm8850 仓，已验证）
- [ ] 合并后验证构建（3 个代表 x）
- [ ] hwid 校验版（`oppo_oplus_realme_all-hwid`）

## 与 cctv18 三仓的差异

1. 5.x 的 SUSFS 源不同：cctv18 的 susfs4oki 无 5.x 分支，改用 ShirkNeko/susfs4ksu
2. 5.x 新增 vendor-fix 步骤（cctv18 在自家源码仓里预先修好）
3. 5.x 不支持 Droidspaces（ntsync 为 6.6+ 特性）
4. 5.10 的 LTO/CFI 修复：5.10 树 `HAS_LTO_CLANG` 依赖 `LLVM_IAS=1`，已加并强制 ThinLTO（对齐 Action-Build 产物形态）
