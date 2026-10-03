# Rldcoin 主计划当前状态

对应主计划与白皮书 1.11。

**目标协议已定义；完整协议资格与实际星际支付服务尚未完成。** [主计划](RLDCOIN_MASTER_PLAN.md)将 I1–I12 定为强制条件，A–G 仍是必需地面基础。完成 A–G 或一次演练都不能自动标记全计划完成。


当前本地候选使用 229 文件冻结源码 `daf6710c8170b994990bbcf96251023fd9d72ffc968de17a51a186c6e4c9843f`；重新构建通过，84 项运输检查、34 项进程/控制器检查通过。发送前完成本地证据准备，再绑定新 TLS 挑战；单次认证中避免重复处理同一已检查帧；已完成运输在活动记录达到 32 时有界归档。活动准入仍为 256、归档仍为每节点 4096 文件/256 MiB、每次最多 16 条，不删除待转发证据或原生账本记录。三秒套接字时限不表示整次迭代或密码验证 CPU 上限。

[保留付款恢复阶段](operations/evidence/regional-native-bft-retained-maturity-20261001.json)已完成，耗时 589.121 秒：从上一轮失败目录的隔离副本启动十二个普通节点，不新签或入队用户付款，原笔净额 9 在高度 10 导入、到高度 12 成熟。成熟观察耗时 144.786 秒，暂停新签名后已有完整证书在 12.163 秒内收敛；停止后每地区四副本高度一致为地球 15、比邻星 12、仙女座 12，发行 300 = 可流通 300 + 在途 0，原出口扣除与导入墓碑保留。4,256 条档案载荷重新认证通过，原失败目录和精确冻结源码保持不变，十二个节点已停止。另行[四份原生收款重放](operations/evidence/regional-bft-retained-cold-recipient-20261001.json)均确认原输出 9 可花、终局覆盖且未隔离；只读重放未改变私有文件。

恢复阶段不是完整故障配置的通过结果。前一轮 [956.535 秒故障演练](operations/evidence/regional-native-bft-preconnect-sustained-20261001.json)虽已完成导入，但未在 600 秒内成熟，失败记录继续保留；完整故障冷验证器实际拒绝把新恢复阶段当作完整通过。相同新冻结源码的[完整新故障配置](operations/evidence/regional-native-bft-early-archive-fresh-20261001.json)已在 863.055 秒内完成：从原高度 7/4/4 起步，地球验证者 0 离线、地球与比邻星双向连接切断；在线验证者在 107.403 秒内通过高度 9 关卡，重启节点在 34.281 秒内追赶，连接于 248.496 秒恢复。原净额 9 在高度 11 唯一导入、13 成熟，恢复后成熟关卡用时 488.991 秒，停签后证书收敛用时 26.455 秒。停止后四副本各自一致为地球 15、比邻星 13、仙女座 16，发行 300 = 可流通 300 + 在途 0。[单独冷验证](operations/evidence/regional-native-bft-early-archive-fresh-cold-20261001.json)完成十二份原生重放、四份原输出成熟检查及 4,506 份归档载荷完整认证，私有文件、原密封起点和冻结源码保持不变，控制器生成共识消息/搬运价值证明/安装检查点均为零。所有观察关卡在记录时限内完成；这是一次同主机、同控制者、有限高度地面配置通过，不能宣称持续 BFT 活性或独立资格。[修订 17 精确源码与报告](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-bft-fault-recovery-v17)已公开；[53 个远端文件校验](operations/evidence/regional-native-bft-v17-publication-verification-20261001.json)全部与本地一致。此前修订 16 和四轮失败保持原样。[官网修订 17 入口](https://rldcoin.com/developers#reproduce-v17)已上线；生产构建、六项状态检查、五个实际页面、精确源码链接和桌面/手机显示均验证通过，旧入口保留，旧接口已删除；测试网接口独立运行。

当前新增原生前缀重放候选：只复用本进程在同一完整信任绑定下已完整验证的精确前驱状态，冷启动仍从创世验证全部保留区块，新尾块仍完整验签/执行，拒绝时不推进终局。去除每块整链复制和时代准备时整份证据复制，为分层历史保存减少重复工作；256 块/64 检查点容量仍保持，20 万块时代与长期恢复尚未完成。[230 文件精确冻结源码检查](operations/evidence/regional-native-prefix-frozen-checks-20261001.json)已完成，源码集合 `47b07d586f58914881c98e32dd7abc93b8cdbfb449b7d6f15538594dd95ecd62`、原生实现 `d268bd83be7f87afa2db26603ae4597d711aa85eaaf265bccdce8d1426b2e971`；86 项原生、84 项运输、34 项进程/控制器检查及严格静态检查通过。[64 检查点样本](operations/evidence/regional-native-prefix-replay-sample-20261001.json)的冷验证执行 64 块，从创世逐份重放的对照执行 2,080 块，所有账本字段和根一致；两个计时工作负载的证书检查范围不同，不能宣称端到端吞吐按同比例提高。[新创世往返](operations/evidence/regional-native-prefix-fresh-cycle-20261001.json)完成 15 次守恒检查，四副本高度一致为 7/4/4，净收款 96/91/86；[停止后冷验证](operations/evidence/regional-native-prefix-fresh-cycle-cold-20261001.json)完成十二份原生重放、十二份历史原输出核查和 1,472 份档案认证，首笔/续转原输出已花、返程原输出 86 可花，私有文件保持不变。[完整新故障配置](operations/evidence/regional-native-prefix-fresh-fault-20261001.json)在 1,059.417 秒后失败：恢复后 600 秒成熟观察超时，部分 BFT 持久状态达到 32 MiB 容量。停止后十二份重放高度为 16/16/17，各地区四副本高度相等；原净额 9 在比邻星高度 15 导入、须高度 17 成熟，当前高度 16 尚不可花。[单独诊断](operations/evidence/regional-native-prefix-failed-fault-diagnostic-20261001.json)确认四份原输出均保留且未隔离，私有文件保持不变；完整故障冷验证器实际拒绝失败报告。重复快照约 32 MB、不同完整快照不足 0.6 MB，仅为字节诊断，不能证明是唯一失败原因；另有锁竞争和 TCP 保管拒绝。下一步实现有界共享证据存储，不能增加上限或删证据取得通过。公开修订 17 及其旧原生实现保持不变。[分层历史义务](research/REGIONAL_HISTORY_RETENTION_V1.md)另列真正长期容量、永久去重与恢复要求。 [修订 18 源码与成功/失败报告](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-prefix-replay-v18)已公开，[44 个远端文件](operations/evidence/regional-native-prefix-v18-publication-verification-20261001.json)均匹配；[官网修订 18](https://rldcoin.com/developers#reproduce-v18)已上线，五个页面、六项状态检查、精确链接及桌面/手机显示验证通过。完整故障失败在官网明确展示，旧入口和修订 17 历史链接保留；旧接口已删除；测试网接口独立运行。

新增本地共享证据存储候选：按完整规范快照字节共享，保留每份信封的有序/重复引用、原始正文、价值/本地标记和完整字节摘要。组合状态仍为 32 MiB，上限 512 消息、每信封 64 引用、载荷 3 MiB 不变；完整原生验证仍在收到和重启时执行，旧私有格式拒绝且不改写。13 项存储/真实原生恢复检查与原有 11 项 BFT、5 项控制器检查通过；签名响应在替换前写入失败或成功原子替换后的响应确认丢失注入中，仍由另存 head 精确恢复，不能首次签名；未注入实际 fsync 失败或断电。[2,259 份旧失败消息的字节往返](operations/evidence/regional-bft-shared-evidence-byte-sample-20261001.json)保持正文、完整证据与标记一致，最大状态由 33,529,748 字节表示为 1,628,727 字节；这仅为字节核查，旧私有目录未迁移，不能替代完整故障通过。首份 234 文件冻结源码 `24fb58eda0a3fcea0744b12e6b2587656a1d740ede5c93b25b6a4291133f6042` 已重建并通过 84 项运输、46 项进程/存储检查；完整往返因控制器仍读取旧状态布局而受控中断，实际命令已到达四个地球验证者。正常清理完成，十二份停止后原生读取和 128 份保留控制信封原生认证通过，私有文件未改变；不能计完整往返通过。读取器已改为新格式的有界只读查询，随后另行冻结的最终候选结果见下一段。


最终 234 文件冻结源码 `5ab9e125172125c34ecd81d811c2f00097a59801d7b326afa017559476c52bc0` 已重建并通过 47 项进程/控制器/存储检查；原生和运输源码字节相同，保留先前 86/84 项检查而未重跑。[新往返](operations/evidence/regional-bft-shared-retention-observer-fresh-cycle-20261001.json)完成净额 96/91/86、15 次守恒和四副本高度 7/4/4；[冷验证](operations/evidence/regional-bft-shared-retention-observer-cycle-cold-20261001.json)完成十二份账本、十二份历史原输出、627 条控制消息与 1,408 份档案认证。[完整新故障](operations/evidence/regional-bft-shared-retention-fresh-fault-20261001.json)在 653.438 秒内通过，原净额 9 在高度 12 唯一导入、14 成熟；最终地区高度 15/14/15。[故障冷验证](operations/evidence/regional-bft-shared-retention-fresh-fault-cold-20261001.json)完成十二份账本、四份原输出、1,898 条控制消息与 4,324 份档案认证，300 = 300 + 0，私有文件未变，最大状态 1,378,543 字节。旧失败和首份受控中断均保留；这仅是一次有限同主机配置通过，不能计持续活性、长期历史或独立资格。下一步实现原生分页历史、永久去重和恢复承诺。[修订 19 精确源码和报告](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-bft-shared-evidence-v19)已公开，[47 个远端文件核验](operations/evidence/regional-bft-shared-v19-publication-verification-20261001.json)全部一致。[官网修订 19](https://rldcoin.com/developers#reproduce-v19)已上线，生产构建、六项状态检查、五个实际页面、六份远端源码、手机菜单及精确链接核查通过；旧接口已删除；测试网接口独立运行。截图工具卡住，未完成本轮图片视觉检查，限制保留在[官网核验](operations/evidence/regional-bft-shared-v19-website-verification-20261001.json)中。

## 当前网络

开发与验证使用无货币价值的公开 fixture 测试网。正式网络尚待完成验收和精确签名采用；测试资产与密钥不得进入正式网络。

[测试网验收与缺口](operations/EARTH_FRESH_TESTNET.md)。

## 强制目标进度

| 条件 | 当前可确认范围 | 未完成的强制验收 |
| --- | --- | --- |
| I1 货币与地区身份 | 固定创世/源绑定，mesh 身份与权限分开；通用 fixture 候选离线验证签名准入和精确源码根。 | 正式通用准入、多源信任时代与独立审查。 |
| I2 当地断联自治 | 固定源候选及通用 CLI 在无远程 HTTP 下出块、付款、成熟、重放与安装接触证据。 | 长期/跨设备、故障恢复和正式采用；原已签节点默认五秒刷新未替代。 |
| I3 发行守恒 | 三地区原生候选已检查多金额/多所有者、拆分合并、找零、两地费用、多来源和循环。 | 通道 E、完整故障恢复及独立发行守恒资格。 |
| I4 任意地区转移 | 三个原生候选账本已通过默认中继启动、自动证据验收/导入、多来源付款、再出口和新返程；目录与实际 TCP 两种地面演练分别通过 31 次守恒检查。 | 跨设备持续原生网络、完整地区共识与独立资格；既有采用节点仍是固定源。 |
| I5 再出口与终局组合 | 候选 Export 验证输入创建的当地已准入终局覆盖（旧配置四签；新容错配置准备/提交各三签），并保留祖先依赖。 | 跨重组/故障模型、BFT/独立签名服务资格与正式采用。 |
| I6 真正价值返程 | 候选执行新出口/返程新导入、持久去重和循环重复拒绝；没有释放初始扣除。 | 外部防回滚、完整故障与长期独立验收。 |
| I7 地区终局与信任演进 | 通用候选已有事故保全/隔离、持久签名 Agent、另存 head 的旧备份拒绝、旧新四签共同交接与时代故障保全。明确准入的容错地面配置新增三签准备/提交、持久准备证书锁、认证换轮和区块/终局原子安装；一位初始领导者离线的真实 CLI 演练推进并完成跨区/再出口。 修订 14 已接入显式准入验证者的自动调度和 TLS 控制帧代码；8 项真实原生 companion 检查覆盖另存 head、签前落盘、无私钥恢复、付款队列验收、迟到旧轮证书安装和新投票发送名额；普通启动的四节点 TLS 自主投票/换轮/追赶/重启/当地付款在工作区与冻结源码均完成。 | 跨区自主候选的持续可用性及完整 BFT 活性/故障/重配置、独立资格、恢复授权和独立保管。 |
| I8 原生发现与因果运输 | fixture 普通启动默认目录与固定 TLS 1.3 的 IPv4 中继；59 项运输/套接字检查、8 项中继进程集成保持通过，增量入网、备用路径、连接认证/拒绝降级及无共享运输目录的三原生进程 TLS 价值演练已验证。 | 已采用节点的新版本集成及精确发布、N1–N10 完整资格、跨设备/物理适配、独立加密审查与对抗资源/可用性；物理路线另证。 |
| I9 付款状态 | 通用原生钱包命令已分开当前可花/未成熟/隔离/可再出口金额；签名复核已审阅金额/收件人/精确地区与当前账本/事故；收款独立验出口、净额、导入/成熟及原输出已花。持久命令/输入预留与另存 head 已加入；共同付款已支持各方独立审阅、持久部分签名、仅本人输入预留与完整授权组合；本机界面接入付款审阅、显式签名/入块、共同批准文件与独立收款核验；交互提案构造固定绝对有效高度，各方在不同高度仍可审阅同一付款；原生随机加密密钥与完整 Journal 备份/新目录恢复已加入，保留预留且要求另存最新 head；界面可保存加密备份。26 项钱包 Rust 检查及 16 项真实钱包进程/HTTP 检查通过。 | 完整钱包产品（硬件保管、加密保管独立安全资格等）、跨设备多所有者资格、重组下预留/恢复、跨设备与外部防回滚及独立资格。 |
| I10 长期存储与恢复 | 短期归档候选；原生 Journal/事故索引重放、缺失/损坏/超额拒绝和精确修复。 | 外部单调根防旧备份回滚、长期独立档案/容量、去重承诺与升级采用。 |
| I11 长期密码与撤销 | 白皮书定义长期验证义务；候选已验证同算法验证者键时代交接；地面 TLS 已验证固定证书/连接认证、拒绝降级与当地有效期，尚无账本算法迁移。 | 实际算法时代、在途撤销/续认证、星际降级防护/验证期限和独立复核；90 天地面证书不是长期资格。 |
| I12 独立资格与持续服务 | 同控制者跨平台检查及原生地面候选；没有独立完成证据。 | 独立运营/保管和安全复核、持续服务、跨设备钱包恢复/防回滚、费用资源及真实路线。 |

**以上全部为部分实现或未实现，I1–I12 没有一项达到完整资格。** 这张表不得以文档修订、测试数量或运营者网页遥测替代。

## 下一步与完成语义


上述新源码的完整故障配置和停止后原生冷验证已通过，精确源码、真实负载/故障/恢复观察及未完成资格已发布。继续本地有界负载、故障/长期恢复与剩余原生义务的实现，独立与物理资格另行验收。现有四轮失败及其准确源码和检查记录保留在[后续验收顺序](operations/INTERSTELLAR_ACCEPTANCE_QUEUE.md)，不得被恢复阶段覆盖或计为通过。相同正文的新证明仍完整验证后才去重，进度不可用保留为未知，不用较低副本的零在途数抹去较高已认证历史中的扣除。

用户确认目前没有第二台测试主机或独立运营者，继续可验证的本地实现；跨主机、独立保管、完整 BFT 活性/重配置、通道、完整钱包、长期存储/密码与实际物理路线均保持为未完成要求。正式主网另须新签名零发行创世，旧网络和测试余额不得迁移。

[修订 15 三地区自主往返](operations/evidence/regional-native-bft-multiregion-campaign-20260930.json)与[冻结源码复现和失败记录](operations/evidence/regional-native-bft-multiregion-verification-20260930.json)现已完成：十二个普通原生进程使用相邻固定 TLS 接触，自动发现三地区；全部地球进程停止期间，比邻星与仙女座自行导入、成熟、再出口并发起新返程。地球恢复后唯一导入返程并成熟；净收款分别为 96、91、86，最终四副本高度一致为地球 7、比邻星 4、仙女座 4，15 次 I=U+T 检查全部守恒。控制器生成投票、携带价值证明、安装检查点与远端阶段地球调用均为零。保留的工作区版本与 226 文件精确冻结源码的完整结果相同，实际观察耗时、只读重试调用数和三份收款时的完整本地 Journal 观察哈希允许不同；两次运行的 24 个原生目录重新验证通过，账本投影、事件、事故及时代证据一致，观察哈希不是余额根；原 167 个采用源码字节不变。81 项原生、36 项进程/HTTP、70 项运输与严格静态检查记录对应这个 V2/TCP-V3 版本。此前失败及中断演练保留，不计通过。完整 I1–I12、持续 BFT 活性、独立保管及物理路线仍未完成。

当前工作区另有未纳入修订 15 的 V3/TCP-V4 归档改动，2026-10-01 的 78 项运输与 36 项进程/HTTP 检查通过；该新版本的工作区完整三地区往返也已完成，15 次守恒检查通过，并在原进程退出后逐份重新读取验证保留档案；[归档候选报告](operations/evidence/regional-native-archive-workspace-checks-20261001.json)保留精确文件哈希与各节点容量观察。该 V3/TCP-V4 版本的 226 文件冻结源码也已独立重新构建并完成完整往返，78 项运输、36 项进程/HTTP 检查通过；两次运行的 24 个原生目录完整重放一致，冻结运行的 416 条归档载荷在原进程退出后逐份重新认证。[精确复现报告](operations/evidence/regional-native-archive-frozen-verification-20261001.json)和[三个真实 SIGKILL 边界](operations/evidence/regional-native-archive-crash-20261001.json)分别保留源码哈希、容量和恢复观察。进程崩溃演练不证明掉电或跨设备资格；[修订 16 精确源码与报告](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-archive-v16)已公开，36 个新增/更新文件的远端哈希均验证一致；历史包保留。持续负载/故障仍待完成，新版本证据与修订 15 分开，不升级已采用网络。[后续验收顺序](operations/INTERSTELLAR_ACCEPTANCE_QUEUE.md)要求先冻结新源码，完成有界归档、持续负载/故障和跨设备验证，再推进独立保管、通道、完整钱包及长期密码/档案。

[通用地区候选](research/REGIONAL_LEDGER_CANDIDATE_V1.md)的[持久签名与时代修订](research/REGIONAL_SIGNER_EPOCHS_V1.md)通过 35 项原生检查与 128 次 CLI campaign；[当前报告](operations/evidence/regional-native-epochs-campaign-20260930.json)覆盖同机公开 fixture 的四签锁/交接、离线转移/新返程、事故隔离和守恒。签名先落盘，再返回；旧签名目录加保留的最新外部 head 拒签。共同交接保持币根与余额，缺任何签名则停顿，不等于 BFT 或完整防回滚。[默认中继与自动原生导入报告](operations/evidence/regional-native-default-relay-campaign-20260930.json)已补齐候选同一启动流程和三地区自动交付/价值返程；这是无货币价值的目录接触实现，不修改已采用节点。[原生钱包验证](operations/evidence/regional-native-wallet-verification-20260930.json)已补齐命令层的签前核对与独立收件；[持久预留与恢复](operations/evidence/regional-native-wallet-reservations-verification-20260930.json)已补齐单所有者命令层的未包含预算和响应恢复；[实际 TCP 地面适配与验收](operations/evidence/regional-native-tcp-verification-20260930.json)已补齐普通启动的本机 IPv4、多跳保管与断线恢复，三账本演练不使用共享运输目录；[默认 TLS 与连接认证](operations/evidence/regional-native-tls-verification-20260930.json)又补齐独立证书固定、拒绝降级/跨连接重放与地面有效期检查；[独立多所有者签名与组合](operations/evidence/regional-native-group-wallet-verification-20260930.json)又补齐共同付款的单方持久批准、本人输入预留、完整组合与实际跨区收款；[本机钱包界面与恢复边界](operations/evidence/regional-native-wallet-app-verification-20260930.json)进一步接入实际付款、预算与收款阶段；[交互共同提案与固定有效高度](operations/evidence/regional-native-group-proposal-verification-20260930.json)补齐不同高度的同一付款构造/独立批准；[加密密钥与完整备份恢复](operations/evidence/regional-native-encrypted-custody-verification-20260930.json)进一步补齐同机地面保管、预留保持、旧备份拒绝与恢复密钥再次付款；下一步完成跨设备/物理适配与独立加密审查、完整钱包产品及跨设备共同付款/重组恢复；BFT、通道、长期存储/密码和独立资格仍是强制条件。安全取消、流动性垫付和压缩证明可另立提案，但不能替代上述强制功能。

当前文档满足目标对齐（DOC_ALIGNED）。协议资格（PROTOCOL_QUALIFIED）、新地球主网正式采用（EARTH_RELEASE_AUTHORIZED）和具体物理路线资格（PHYSICAL_ROUTE_QUALIFIED）均未完成。各阶段必须记录精确版本、范围、故障假设和期限；不承诺超光速、无限档案寿命或百万年密码安全。

[修订 13 地区容错地面演练](operations/evidence/regional-native-bft-campaign-20260930.json)使用每地区四个账本/签名目录、三名实际 CLI 投票者。初始领导者不投票，三方认证换轮后推进，离线副本逐个认证块追赶；原生钱包完成净额 95 的比邻星收款和净额 93 的仙女座再出口，远端执行期间无地球调用。12 次守恒检查只计算每地区一份规范历史。该修订的控制器携带投票消息，当时普通中继不会自动投票/调度；运输证据保管不能当作当地导入提交。完整自动共识网络、容错时代交接、独立运营/保管及持续故障资格仍未完成，I7 仍为部分实现。

[修订 14 自动 TLS 演练](operations/evidence/regional-native-bft-autonomous-campaign-20260930.json)与[完整验证及失败记录](operations/evidence/regional-native-bft-autonomous-verification-20260930.json)记录普通原生启动的四验证者网络：初始领导者离线时其余三名实际投票者推进到第三块，离线副本经固定 TLS 多跳证据追赶；已审阅签名付款先入队/传播而未扣账；四节点带另存签名 head 重启后自行认证到第五块，副本余额一致、收款净额 30、待入块输入预留为零。控制器生成共识消息和安装检查点次数均为零；逐跳证据验证实际两跳承载。工作区与冻结的 225 文件源码重建分别完成相同语义结果，差异只在声明的阶段实际耗时；每个主要观察阶段上限 300 地面秒，重启/付款阶段分别约 98.391/189.186 秒，均不是星际时效承诺。原有 167 个采用源码字节保持不变。

80 项原生、34 项进程/HTTP、61 项运输测试与严格静态检查在工作区/冻结源码分别通过。新的 8 项自动运行检查覆盖 caller head 精确恢复、签前保存失败、旧备份拒绝、控制帧域、原生付款 JSON/篡改、无私钥旧轮完整证书验收及新投票发送名额。此前超时或控制器字段错误的 8 次初步运行没有计为通过；修复点和观察耗时在验证报告保留。三个地区的原生控制器携带价值回归另保留 12 次守恒检查，旧配置三进程 TLS 另保留 31 次；它们不等于三地区全自动网络。跨地区自治持续服务、完整容错活性/重配置、独立运营/保管、外部单调锚、通道/完整钱包、长期存储/密码与真实物理路线仍未资格化；I1–I12 仍没有一项完整达标。

## 原生分页磁盘存储候选

### 私有账本档案与新目录恢复候选

新增 `history-archive` / `history-restore`，在原生锁内核对另存最新头和完整原生重放。
档案保留全部分页对象、认证事故与损坏事故残留；摘要只核对字节，不授权价值。
目标必须是新私有目录，复制并同步后再次完整核验才移除 `RESTORING`；中断目录
保留不重写，普通启动、钱包入口及事故恢复均拒绝。签名者、钱包、调用者头与待
审核状态、密钥、TLS 和运输档案不在账本恢复范围，也不得公开生成的档案。
十项新增原生测试及严格检查通过；五项真实命令测试通过，包含实际 SIGKILL、
已消费导入的永久记录、旧头/跨域/既有目标拒绝。首轮一项测试的错误文本断言失败
已保留日志与初始源码；改为完整长度伪签名后验证原生密码核验拒绝。当前源码
尚待精确冻结、新 fixture 创世往返与完整有限故障配置，不能沿用修订 20 的通过。
逻辑 8 MiB/256 块/64 检查点与档案边界不变；真正长期历史、独立最新锚、掉电和
跨设备保管仍未完成。

默认节点创建/重启已接入 `RLD-NATIVE-HISTORY-MANIFEST-V1`：完整快照、时代与接触记录保存为不可变规范对象，十六事件页绑定顺序、当地高度区间和前页摘要；紧凑清单承诺完整重建日志，再执行原生币种、终局、所有者、守恒、永久导入和事故核验。旧尾页和失败残留不删除、不作为新价值授权。4,096 文件/256 MiB 的地面档案准入计入所有残留；逻辑 8 MiB、256 块/64 检查点及账本索引上限不变。

调用者另存最新 `history-head` 后，`history-check` 在原生锁内拒绝旧清单，并在原生重放前拒绝待恢复事故；当前查询不代表独立新鲜度，全状态与头一起回滚仍未获资格。首批 12 项新增分页/原生拒绝检查和原有 86 项原生检查通过，严格静态检查通过；原接触记录损坏检查改为摘要自洽的损坏分页对象，并明确验证原生“缺少已认证源检查点”的拒绝，避免只因旧布局被拒而通过。源码改变需要新 fixture 创世/币种，旧私有目录拒绝且保留，不能复用修订 19 的通过报告。后续最终冻结源码已完成真实进程和新签付款往返/停机冷验证，详见本节新增结果；20 万块历史、紧凑远程价值证明和新目录档案恢复仍未完成。

首份 237 文件冻结源码 `b0df4102859ee85f1101ef94b8626446bab4bd5ed7d4c10303ba665f8d218e6f` 已重建，98 项原生检查和严格静态检查通过；52 项进程检查有一项错误，因为测试未显式选取 100 的实际输入，原生守恒正确拒绝，未开始完整往返。第一份源码与日志保留。另用真实认证事故证明复现了历史头未承诺未索引事故的缺口；当前锁内检查已要求全部保留认证事故与清单索引完全一致，拒绝时不重写事故、清单或保管头。追加回归需在新源码下重新完整核验。

最终 237 文件源码 `1756c85e876dbca24275c77e7d035673d2b3fd4a90c5c67b0cbbbf99cd0d445b`、新原生实现 `55342fdef7568fadbd9d0c6d529a081e3ccd490b62b37b3d10e28b900ca773f8` 已从冻结目录重建并通过 99 项原生、52 项进程/存储/历史和严格静态检查；先前 84 项运输检查来自精确相同字节，未重跑。[新往返](operations/evidence/regional-native-history-pinned-fresh-cycle-20261001.json)完成净额 96/91/86、十五次守恒和四副本高度 7/4/4 一致。[冷验证](operations/evidence/regional-native-history-pinned-cycle-cold-20261001.json)认证十二份原生重放、十二份历史原输出、639 条保留控制信封和 1,424 份运输档案；[原生分页核查](operations/evidence/regional-native-history-pinned-cycle-storage-audit-20261001.json)完成十二次新进程完整重放和精确另存头匹配，最大清单 4,522 字节、最大逻辑日志 165,304 字节，私有文件与冻结源码不变。短往返每副本仅一事件页，不能认证长期执行。[完整新故障配置](operations/evidence/regional-native-history-pinned-fresh-fault-20261001.json)已在 723.342 秒内通过并正常退出，原净额 9 在比邻星高度 12 唯一导入、14 成熟，最终地区四副本高度 14/14/16；[单独故障冷验证](operations/evidence/regional-native-history-pinned-fault-cold-20261001.json)认证十二份原生重放、四份原输出、1,922 条控制消息和 4,359 份运输档案，300 = 300 + 0；[分页核查](operations/evidence/regional-native-history-pinned-fault-storage-audit-20261001.json)完成十二次完整重放和精确另存头匹配，每副本两事件页、最大清单 6,791 字节、最大逻辑日志 434,232 字节，私有文件和源码不变。[首份附加核查的工具失败](operations/evidence/regional-native-history-pinned-audit-tool-failure-20261001.json)在首次原生调用前发生，缺失的顶层报告币种字段现由精确 bootstrap/报告绑定替代；修复后通过，原生源码未变。逻辑上限和残留准入不变，既往失败源码/记录保留；这是一次有限同主机配置观察，仍不认证长期历史、独立最新锚、完整 BFT 或物理路线。

[修订 20 精确源码、通过/失败记录及复现命令](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-01/regional-native-paged-history-v20)已公开，[54 个远端文件核验](operations/evidence/regional-native-history-v20-publication-verification-20261001.json)全部逐字节匹配。独立英文[官网修订 20](https://rldcoin.com/developers#reproduce-v20)已上线，提交 `679911eabc6ee14733a5150669db23b15558e184`、生产部署 `dpl_5FPGFgtnSgHbe7LdtcEGXCvMuvyJ` 为 READY；[官网核验](operations/evidence/regional-native-history-v20-website-verification-20261001.json)完成生产构建、六项状态检查、五个线上页面、六份精确远端源码、桌面/手机实际画面及菜单/跳转核查，未见横向溢出或浏览器错误。命令行截图超时，诊断后改用应用内浏览器成功保存和检查画面；本轮视觉记录已完成。旧复现锚及修订 19 通过、18 失败、17 历史直达链接保留；旧接口已删除；测试网接口独立运行。本轮临时浏览器/本地网站服务和演练节点均已正常关闭，私有状态保留，论坛未发消息。下一步继续真正长期原生执行、独立最新锚和带中断标记的新目录恢复，而不是提高现有上限或宣称跨主机/物理资格。

新私有账本恢复候选的 241 文件精确源码 `4af70053f541a67f967bbcfca3d647c46af663343c34e76d7c2e5d63cee6d258`、原生实现 `d713c6afc275d743b50059250815617b4a88bc97eef201c4d6ee18ab9cf80e6d` 已冻结重建，109 项原生、57 项进程/历史检查和严格静态检查通过。新签 fixture 往返完成 96/91/86、十五次守恒与四副本高度 7/4/4；[单独冷验证](operations/evidence/regional-native-history-image-cycle-cold-20261002.json)认证十二份原生和原输出、607 条 BFT 信封、1392 份运输档案，私有文件不变。[十二份新目录恢复](operations/evidence/regional-native-history-image-cycle-fresh-target-audit-20261002.json)全部完整原生重放、另存头、状态/永久导入/事故及所有保留字节匹配，源文件和冻结源码不变，档案私有且不包含签名者、钱包或调用者保管状态。完整新有限故障配置已启动，但尚无终端通过结果；未公开修订 21，也未将修订 20 报告计作新源码资格。长期历史、独立最新锚、掉电和跨设备资格仍未完成。

当前原生档案恢复源码的[完整新有限故障配置](operations/evidence/regional-native-history-image-fresh-fault-20261002.json)已在 583.24 秒通过并正常退出，原净额 9 在比邻星高度 11 唯一导入、13 成熟；最终地区四副本高度 {'earth': 14, 'proxima': 13, 'andromeda': 14}。所有演练进程已停止，原封存周期目录不变。[单独故障冷验证](operations/evidence/regional-native-history-image-fault-cold-20261002.json)认证十二份原生、四份原输出、1688 条 BFT 信封和 3844 份运输档案，原私有文件不变；[十二份故障账本新目录恢复](operations/evidence/regional-native-history-image-fault-fresh-target-audit-20261002.json)全部原生完整重放、另存头、状态/永久导入/事故和保留字节精确匹配，源文件与冻结源码不变。加上周期共 24 份私有账本档案/恢复已通过，但不恢复签名者、钱包或调用者保管状态，不公开生成档案。一次同机有限配置和真实进程中断不等于掉电、独立最新锚、跨设备保管、长期历史或全部 I1–I12 资格。

[修订 21 私有账本恢复精确源码与验收记录](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-02/regional-native-history-recovery-v21)现已公开，提交 `dbb9930eb74819b8b2403010baa530eb3b4d6e20`，50 个远端文件逐字节匹配。独立英文[官网修订 21](https://rldcoin.com/developers#reproduce-v21)已上线，提交 `56f5ccd4614a69e36d3b883bb18c651290a50134`，生产部署 `dpl_7zErQPk49YHuA3cGwV4V9xUsxUuX` READY；五个线上页面、六份远端源码、六项状态检查、桌面与手机实际画面及导航核验通过，没有横向溢出或浏览器错误。生产域名确实服务新固定源码版本，旧 14–20 复现入口与 v20/19/18/17 历史证据直达链接保留。Vercel 连接器读取团队时返回 403，现有项目 CLI 授权可正常读取并核对准确部署、提交和域名；没有扩展权限或重新配置账号。首个远端文件核验发生瞬时 Broken pipe，保留失败记录后按原 TLS 核验重试，完整 50 文件核验通过。临时浏览器已关闭、视口恢复；旧接口已删除；测试网接口独立运行，论坛未发消息。继续真正长期原生执行、紧凑远程依赖证明和永久索引扩展；独立锚、掉电、跨设备保管与物理资格保持未完成。


继续推进长期历史的结构性限制：原生存储 V2 以准确的已列前置检查点对象复用磁盘前缀，后续对象只保存新增块及完整证书/时代信息。读取时拒绝前向、孤立、跨域、长度/高度不符的引用，限制展开字节并重建完整原生日志后核验。完整签名运输快照及价值规则不变；源码承诺变化仍要求全新签署的无价值 fixture。旧 V1 私有目录和所有历史记录保留，不能自动升级或迁移余额。逻辑 8 MiB/256 块/64 检查点与 4096 文件/256 MiB 档案准入均不提高；这是重复磁盘历史的改进，不是长期历史或紧凑远程证明完成。新增六项原生测试正在核验，最终冻结、新 fixture 往返与故障资格尚待本轮结果。

The first frozen disk-prefix candidate exposed an unintended duplicate-checkpoint refusal in complete regression. Exact repeats and independently authenticated equivalent BFT quorum encodings remain valid native evidence. Storage now retains every listed proof and selects the earliest exact predecessor object for deterministic prefix sharing; it does not normalize away native authorization checks. The first full frozen source and failed logs are retained; a seventh focused regression covers exact repeats and forged duplicate rejection. Final frozen qualification is pending.


最终磁盘前缀候选的 242 文件源码 `a108ec7da7e8707d0c46093e33af64ae6893fb2529ea22eb5a773e0a23a1d928`、原生实现 `64c09ec0696918b42f0c91fe82cb66c9ea833e1e205d873f89d9174bad24a2a6` 已冻结重建，116 项原生、57 项进程/历史检查与严格静态检查通过。[64 检查点样本](operations/evidence/regional-native-history-prefix-final-storage-sample-20261002.json)将准确相同快照的 V2 对象字节从 1314584 降至 149192，约减少 88.65%；完整原生日志及新目录档案恢复精确一致。这不表示运输/内存或全部残留同幅减少。新签 fixture 往返完成 96/91/86、十五次守恒和地区各四副本 7/4/4；[停机冷验证](operations/evidence/regional-native-history-prefix-final-cycle-cold-20261002.json)与[十二份新目录恢复](operations/evidence/regional-native-history-prefix-final-cycle-fresh-target-audit-20261002.json)通过，私有原件和冻结源码不变。完整新有限故障配置已启动，尚无终端通过结果；首份源码与 87 通过/28 失败日志另存，不沿用修订 21 的资格，未公开修订 22。所有原边界及长期历史/紧凑远程证明/独立最新锚/掉电/跨设备资格仍未完成。


当前最终磁盘前缀源码的[完整新有限故障配置](operations/evidence/regional-native-history-prefix-final-fresh-fault-20261002.json)在 705.36 秒通过并正常退出，原净额 9 在比邻星高度 12 唯一导入、14 成熟，最终地区各四副本高度为地球 15、比邻星 14、仙女座 15。所有演练节点停止，封存周期原件不变。[单独故障冷验证](operations/evidence/regional-native-history-prefix-final-fault-cold-20261002.json)完成十二份原生和四份原输出核验，认证 1918 条 BFT 信封与 4352 份运输档案，私有原件不变；[十二份故障账本新目录恢复](operations/evidence/regional-native-history-prefix-final-fault-fresh-target-audit-20261002.json)完整原生重放、准确另存头、状态/永久导入/事故及每份保留字节一致。加上周期，24 份私有账本档案与恢复通过；不含签名者、钱包或调用者保管状态，生成档案不公开。第一次冻结的 87 通过/28 失败与准确源码保留；修正后最终 116 项原生、57 项进程检查通过。V2 减少重复磁盘历史，完整运输与内存、原边界保持；长期历史、20 万块时代、独立最新锚、掉电、跨设备及物理/独立资格仍未完成，目标继续。


[修订 22 准确源码与通过/失败证据](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-02/regional-native-history-prefix-v22)已公开，提交 `3decd2ac98a52945395de0774cec42240cc91cfb`；[远端核验](operations/evidence/regional-native-history-v22-publication-verification-20261002.json)确认 52 个远端文件逐字节一致、main 指向该提交，公开工作区干净。包包含最终 242 文件源码及第一次失败的完整 242 文件源码/日志/说明，没有生成的私有账本、密钥、钱包、签名者、调用者、TLS 或运输保管状态。独立英文官网当前保留修订 21 的准确固定版本入口，本轮集中于本地实现与公开源码；没有发论坛消息。所有演练节点已停止，源/档案/恢复原件保留。继续紧凑远程证明、完整内存/永久索引扩展和超越 256 块/64 检查点的长期原生执行；未认证跨主机、独立最新锚、掉电、跨设备保管、物理路线或全部 I1–I12，目标保持进行中。


下一阶段已接入原生接触 V2 与 BFT 网络 V2 的消息内检查点前缀共享：只引用同一消息中已出现的准确前置检查点，重建完整 Evidence 后继续原生签名、终局、时代、所有者、守恒和永久导入核验。完整本地 Evidence/Journal 序列化与签名消息不变；BFT 提案/终局消息体仍完整。原生打包命令先核验逻辑信封，接收/冷启动核验返回完整原生证据供 Python 同步，排队命令不扣款。3 MiB 物理载荷和 8 MiB/256 块/64 检查点逻辑边界不提高，旧 V1 载荷拒绝且无回退，需要新签无价值 fixture。首轮接触测试 8 通过/1 失败是测试重投递仍编码旧格式；源码片段与日志保留后改用真实当前载荷。首轮完整原生回归 121 通过/1 失败，是新 BFT 成本测试未经测量地要求至少减半；改为验证准确前缀、完整冷核验和实际字节减少，并记录真实成本，不作任意倍数承诺。最终冻结/进程/新签往返与完整故障资格尚待结果；真正长期执行、永久索引/紧凑状态证明、独立最新锚和物理资格仍未完成。

The first complete 244-file carriage freeze passes all 122 native tests but strict clippy rejects an explicit loop counter in the expansion-limit test. The full frozen source and logs remain retained; the test now uses an explicit height range without relaxing bounds or warnings. Final source qualification is pending, with no process/cycle/fault pass transferred from the first freeze.


最终紧凑证据运输候选的 244 文件源码 `b49b62072387b63720c64edc324788884ca117c45147166f69f2a9583ca692f0`、原生实现 `e213d670da01c99ea34706a15b1f241d3bf5bbd137ca95d107f5a9b5841d6918` 已冻结重建，122 项原生、57 项进程、85 项重新运行的运输检查及严格静态检查通过。新签无价值 fixture 的完整三地区往返通过，净额 96/91/86、十五次守恒和地区四副本高度 7/4/4；单独周期冷核验与十二份账本新目录恢复通过，私有原件和冻结源码不变。完整新有限故障配置正在运行，尚无终端结果；修订 23 未发布，不能沿用修订 22 或首份冻结源码的资格。首份完整冻结的严格检查失败和两份较早原生源码片段/测试失败日志都保留。3 MiB 物理载荷、8 MiB/256 块/64 检查点原生逻辑边界及签名消息体不改变；真正长期执行、紧凑状态证明、永久索引、独立最新锚、掉电/跨设备和物理资格保持未完成。


最终紧凑证据运输源码的[完整新有限故障配置](operations/evidence/regional-native-carriage-final-fresh-fault-20261002.json)在 560.168 秒通过并正常退出，原净额 9 在比邻星高度 10 唯一导入、12 成熟；最终地区各四副本高度地球 13、比邻星 12、仙女座 13，所有自建节点已停止，封存周期原件不变。[单独故障冷核验](operations/evidence/regional-native-carriage-final-fault-cold-20261002.json)完成十二份原生与四份原输出核验，认证 1,674 条 BFT 信封及 3,827 份运输档案，私有文件不变。[故障账本新目录恢复](operations/evidence/regional-native-carriage-final-fault-fresh-target-audit-20261002.json)十二份完整原生重放、准确另存头、状态/永久导入/事故及每份保留字节一致；加上周期共 24 份私有账本档案与恢复通过，源文件与冻结源码不变。不恢复签名者、钱包或调用者保管状态，生成档案不公开。最终 122 项原生、57 项进程、85 项运输重新运行及严格检查通过，旧失败来源/日志保留。消息内前缀共享减少重复载荷，原生完整认证、签名消息体及原边界保持；真正长期执行、紧凑状态证明、永久索引扩展、独立最新锚、掉电/跨设备及物理资格仍未完成。修订 23 公开复现包正在整理，尚未宣称远端发布。


[修订 23 准确源码与复现证据](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-02/regional-native-proof-carriage-v23)已公开，提交 `1ed5cc11598b11e2d5d38b12fedff33b39ba0a4b`；[远端核验](operations/evidence/regional-native-carriage-v23-publication-verification-20261002.json)确认 main 指向该提交、全部 58 个变更文件逐字节相同。57 文件复现包含完整最终及首份失败的 244 文件源码、两份原生源码片段、失败日志与准确检查/周期/故障/恢复报告。全部四个归档仅包含已审查源码，生成私有账本/密钥/钱包/签名者/调用者/TLS/运输保管材料未公开。独立英文官网仍固定修订 21 的历史复现入口，本轮未修改网站或发论坛消息。演练进程已全部停止，私有原件保留，目标继续推进长期原生执行和紧凑状态证明；跨主机、独立最新锚、掉电、跨设备保管、真实物理路线及全部 I1–I12 仍未完成。


新状态证明候选已将原生块/检查点状态根接入有序输出、导出和永久导入索引及发行/收到总量承诺。成员证明绑定准确记录和位置；不存在证明要求完整认证的相邻键或准确首尾边界。原生命令必须先完整重放调用者指定的认证检查点，并绑定记录类别与键；历史成员不表示当前可花，证明不导入、不签名、不扣款。六项新增回归验证篡改、范围/路径/类别/计数/容量拒绝以及真实所有者导出、已消费导入和冷重放。第一份候选全套 128 原生测试通过，但严格检查拒绝两项代码问题；准确原生源码片段和日志保留，已修正为间接分配的证明成员及原生整除检查，严格检查通过。4,096 条合成记录的不存在证明样本为 2,683 字节，对比完整合成状态 860,228 字节；这是索引形状/字节成本观察，不是发行或长期历史资格。源码改变后需要全新 fixture 创世/币种，最终冻结、真实进程、新签往返和完整故障核验仍待完成。当前生成证明仍重建有界整表，完整 Evidence 和原生历史仍必需；未提高 4,096 索引及 256 块/64 检查点/8 MiB 等边界，不宣称增量永久索引、紧凑完整远程价值授权或长期执行完成。


最终状态证明候选的 247 文件源码 `f0586e230a2f6f3b3cd13187d214c9c3a0c9acc5aa396ce2036e8ad7e51472ab`、新原生实现 `df0a2c8f1faf93273a9be0212021575879a1f01cc39b0c614ae1031600b4281f` 已冻结重建；[最终检查](operations/evidence/regional-native-state-proof-final-frozen-checks-20261002.json)确认 128 项原生、59 项真实进程/历史/状态证明检查与严格静态检查通过。两项新增真实命令验证指定检查点/键/类别、篡改与未知检查点拒绝，以及真实所有者跨区付款的已消费原输出不存在证明、永久导入成员证明、新私有档案恢复后完整原生核验和再次导入拒绝；查询/拒绝不改变原私有文件。85 项运输检查来自修订 23 精确未变的运输字节，本轮未重跑，不冒称新运行。当前全新签署的 fixture 三地区往返已启动，完整终端结果、单独冷核验、新目录恢复及完整新故障配置仍待完成；状态证明候选未公开，修订 23 资格不沿用。原生完整历史/Evidence 和原边界不变，增量永久索引、紧凑完整远程授权及真正长期执行仍未完成。


最终状态证明源码的[全新 fixture 三地区往返](operations/evidence/regional-native-state-proof-final-fresh-cycle-20261002.json)已正常通过：净额 96/91/86、十五次守恒、地区各四副本高度 7/4/4，远端继续转出与返回时全部地球节点停机，控制器投票/携带付款证明/安装检查点均为零。[单独周期冷核验](operations/evidence/regional-native-state-proof-final-cycle-cold-20261002.json)及[十二份新目录账本恢复](operations/evidence/regional-native-state-proof-final-cycle-fresh-target-audit-20261002.json)通过，私有原件和冻结源码不变。当前独立私有复制目录的完整新有限故障配置已开始；尚无最终故障资格或修订 24 公开发布结果。签名者、钱包、调用者和运输/TLS 保管状态不随账本恢复，生成档案不公开；真正长期执行、增量永久索引、完整紧凑远程授权、独立最新锚、掉电/跨设备及物理路线仍未完成。


最终状态证明源码的[完整新有限故障配置](operations/evidence/regional-native-state-proof-final-fresh-fault-20261002.json)已在 539.07 秒正常通过：原净额 9 在比邻星高度 11 唯一导入、13 成熟；最终地区四副本高度地球 13、比邻星 13、仙女座 14，所有自建节点停止，封存原周期不变。[单独故障冷核验](operations/evidence/regional-native-state-proof-final-fault-cold-20261002.json)认证十二份原生状态、四份原输出、1,699 条 BFT 信封和 3,861 份运输档案，私有文件不变；[十二份故障账本新目录恢复](operations/evidence/regional-native-state-proof-final-fault-fresh-target-audit-20261002.json)完整原生重放、准确另存头、全部状态/永久导入/事故及保留字节一致，源文件与冻结源码不变。加上周期共 24 份私有账本档案/恢复通过；不恢复签名者、钱包、调用者及运输/TLS 保管状态，生成档案不公开。最终 128 原生/59 进程及严格检查通过，85 运输来自准确未变字节的既有运行、本轮未重跑。首次 128 原生通过但严格检查失败的原生源码片段/日志保留，准确 scope 不冒称完整 workspace 冻结。只读诊断曾观察到单个比邻星副本的导入和锁占用未知状态；诊断未改变演练参数或构建共识/付款证明，完整结果来自正常终端通过及单独冷核验。公开复现包正在核查，修订 24 尚未宣称远端发布；真正长期执行、增量永久索引、完整紧凑远程授权、独立最新锚、掉电/跨设备与物理资格仍未完成。


[修订 24 原生状态记录证明准确源码与复现证据](https://github.com/RunlaiDeng/rldcoin-genesis/tree/main/research/2026-10-02/regional-native-state-proofs-v24)已公开，提交 `e4cebd7e3d60c2e1edd4ed06ada6abeb69db9800`；[远端核验](operations/evidence/regional-native-state-proofs-v24-publication-verification-20261002.json)确认 main 指向该提交、全部 56 个变更文件逐字节相同，公开工作区干净。包包含准确 247 文件源码、31 文件原生源码片段、保留日志和最终 128 原生/59 进程/完整新往返/539.07 秒故障/冷核验/24 份私有恢复记录。两份原始测试日志保留末尾空行，引起通用空白检查提示；准确核对原日志（仅声明的工作区路径脱敏）后，源码与文档范围检查通过，没有删改日志字节或放宽原生严格检查。全部生成的私有账本档案、密钥、钱包、签名者、调用者、mesh/TLS 和运输保管状态均未公开，全部演练进程停止。独立英文官网仍保留修订 21 固定历史入口，本轮未改网站或发论坛消息。新状态根及成员/不存在证明是长期历史的基础，完整原生 Evidence 与历史仍必需；下一步推进有界活动历史与增量永久索引，不能仅提高 256 块/64 检查点/4,096 索引边界。20 万块时代、完整紧凑远程价值授权、独立最新锚、掉电、跨设备保管、独立运营及真实物理路线保持未完成，目标继续。


已加入单独的原生档案流式重放候选：从调用者固定的新签 fixture 创世逐块执行，普通节点与游标共用所有者/守恒/导入/发行内核，不能从序列化缓存余额启动。初步五项聚焦检查中，1,032 块、1,024 次真实签名付款、净额 59 的延迟返回导入和重复导入拒绝样本已在冷重放得到相同结果，最多保留 256 个历史观察；最终冻结与命令行/完整回归仍待完成。命令只读核验私有档案和另存准确头，不采用账本或恢复签名，明确不处理事故隔离；初始一致 PoW 之外的 BFT/本地时代切换拒绝。普通存储/钱包/签名者/检查点的 256 块/64 快照、4,096 索引、8 MiB 逻辑及 256 MiB 档案边界不提高。首轮测试编译因不可用 uuid 测试引用失败，准确原生源码片段和日志保留，改用既有唯一测试目录生成器后通过原四项测试。真正普通节点长期运行、增量永久索引、20 万块时代和独立资格仍未完成。

五项流式聚焦检查通过，额外验证私有权限/链接、损坏格式、8 MiB 记录和 256 MiB 档案容量拒绝，拒绝保留原字节。严格检查发现新 Record 的较大枚举字段，准确源码片段与日志保留后改为间接分配 Block；序列化和原生规则不变，严格检查通过。最终源码冻结、全部原生回归、真实命令行核验和新签无价值三地区往返即将运行，不沿用旧源码资格。


最终流式档案重放候选的 250 文件源码 `1593d355e4bf94514ce596c06aaaae0c58b0464fe1e8ecb788f646d594073b53`、原生实现 `601b7153fe673292ede3c23ced9f765d0e4cd572532f0e9563f3cf01664cafe8` 已冻结重建。[133 项原生和 59 项进程检查](operations/evidence/regional-native-stream-replay-final-frozen-checks-20261002.json)与严格检查通过；[长档案样本](operations/evidence/regional-native-stream-replay-final-stream-sample-20261002.json)重放 1,032 块、1,024 次真实所有者签名付款，私有档案 1,338,021 字节，只保留 256 个历史观察，延迟返回导入净额 59、永久重复导入拒绝与冷重放一致，真实命令行入口亦通过。[规则正文对照](operations/evidence/regional-native-stream-replay-final-kernel-review-20261002.json)确认共用执行规则仅替换已推导上下文字段。原生测试终端通过后，汇总控制器变量出错；[恢复记录](operations/evidence/regional-native-stream-replay-final-controller-resume-20261002.json)绑定成功日志和保留脚本，源码不变且已通过测试不重复。

[新签 fixture 三地区往返](operations/evidence/regional-native-stream-replay-final-fresh-cycle-20261002.json)正常通过净额 96/91/86、十五次守恒、地区各四副本高度 7/4/4；远端继续转出与返回时地球全停，控制器投票/携带证明/安装检查点均为零。[单独冷核验](operations/evidence/regional-native-stream-replay-final-cycle-cold-20261002.json)及[十二份私有账本新目录恢复](operations/evidence/regional-native-stream-replay-final-cycle-fresh-target-audit-20261002.json)通过，全部演练进程停止，私有原件和冻结源码不变。本源码未重跑完整故障配置，不沿用修订 24 故障资格；85 项运输检查来自精确未变源码的既有记录，本轮未重跑。当前长重放是只读初始一致 PoW 档案核验，不处理事故隔离、不采用账本、不恢复签名，普通节点/快照/BFT/钱包仍保留原历史边界。公开修订 25 复现包正在核验，尚未宣称远端发布；普通节点有界长期运行、新长期终局、增量永久索引、20 万块时代、独立最新锚/档案及物理资格仍未完成。
