# 跨区域离线证据传输（Earth 现有协议，非星际上线记录）

此操作层衔接正式 Earth 源区与零原生发行的目的区节点。接触可来自文件、物理介质或未来 BPv7 承载。`tools/interstellar_transfer.py` 只固定路线、限制大小、哈希绑定原始证据、持久入队并交给节点验证；帧 ID 不是来源身份认证或到账证明。节点的已签创世与源码承诺仍是价值权限边界。该工具在创世源码承诺以外，改动它不构成共识升级。当前所有已验证节点与签名人仍由单一所有者控制，尚无远方物理链路。

## 顺序和状态

1. 付款人签署指向正确目的区的源区 `Export`。源区在选定链记录锁定，等待至少 12 次源确认。四把持久锁定的密钥签署终局证书，并在源区节点安装。保存源历史、出口命令、证书及其独立验证结果。
2. 通过 `capture-sync --kind source-sync` 截取从固定源锚到终局点的有界选定链页；通过 `pack --kind source-finality` 封装原始证书。用现有 `earth-f-import` 根据独立重放的源区历史、命令和证书生成 `FinalizedImport`，再用 `pack --kind finalized-import` 封装。每个帧固定源/目的链 ID 和出口 ID，消息 ID 对精确载荷字节计算；签名仍由原证书和命令提供。
3. 每个接触端用 `receive` 先落盘并同步，再用 `carry` 复制精确字节。重复接收同一帧返回 `new: false`，队列上限拒收新帧但不删除旧帧。接触中断时原始帧仍在队列；记录外部接触日志、容量和交付确认。帧生命周期或路由失败不解锁源区价值。使用 BPv7 时，这些帧可作为束载荷，按 RFC 9172 保护束层完整性/保密性；接触、保管与对端认证仍须单独配置和验证。RFC 9171 不规定强制逐跳保管，RFC 9172 不提供逐跳认证服务。当前工具不是 BPv7 实现。
4. 远端的**本地源副本**按顺序 `apply` 源历史页和终局证书；本地目的区节点从这个副本同步，然后 `apply` 导入命令。两节点重放并拒绝错误身份、工作、状态根、签名、证明、重复出口或未终局检查点。导入提交返回值只说明命令处理结果；必须另外观察选定目的链导入和至少六个本地区块成熟，收款人才可称为可花。
5. 目的区 `capture-sync --kind destination-sync` 截取返程区块，`capture-receipt` 取得本地导入收据并再次本地验证达到 `recipient_spendable_height`。导入高度 91 对应可花高度 97；若确认数包含导入区块本身，则高度 96 的 6 次确认尚未可花，至少要高度 97 的 7 次确认。经相同持久队列返程。源侧需运行绑定**同一目的区创世**的本地目的区副本，先重放收到的目的区块，再 `apply` 收据。收据只是索引，只有该副本同时重放源/目的历史并在当前选定分支核验后，才得出本地验证结论；无返程接触时维持“远端结果未知”。

典型命令形状（`SOURCE`、`DEST`、`EXPORT`、`SOURCE_ANCHOR`、`DEST_GENESIS` 均从签名发布和节点复核；`127.0.0.1` 是各区域各自的本机节点）：

```text
python3 tools/interstellar_transfer.py capture-sync --kind source-sync --source-chain "$SOURCE" --destination-chain "$DEST" --export-id "$EXPORT" --origin http://127.0.0.1:SOURCE_PORT --anchor "$SOURCE_ANCHOR" --from-id "$SOURCE_ANCHOR" --output-dir ./outbound
python3 tools/interstellar_transfer.py pack --kind source-finality --source-chain "$SOURCE" --destination-chain "$DEST" --export-id "$EXPORT" --payload-file ./source-finality.json --output ./source-finality.frame.json
python3 tools/interstellar_transfer.py pack --kind finalized-import --source-chain "$SOURCE" --destination-chain "$DEST" --export-id "$EXPORT" --payload-file ./finalized-import.json --output ./import.frame.json
python3 tools/interstellar_transfer.py receive --source-chain "$SOURCE" --destination-chain "$DEST" --queue ./custody --input ./import.frame.json
python3 tools/interstellar_transfer.py carry --source-chain "$SOURCE" --destination-chain "$DEST" --queue ./custody --message-id "$MESSAGE_ID" --output ./contact/import.frame.json
python3 tools/interstellar_transfer.py apply --source-chain "$SOURCE" --destination-chain "$DEST" --input ./contact/import.frame.json --destination-origin http://127.0.0.1:DEST_PORT
```

同步页 `apply` 须带 `--anchor "$SOURCE_ANCHOR"` 或 `--anchor "$DEST_GENESIS"`，并分别带 `--source-origin` 或 `--destination-origin`。终局证书帧用 `--source-origin`；导入和收据帧用 `--destination-origin`。顺序必须满足当地源重放、终局安装、目的源视图刷新、导入、成熟、返程目的历史重放、返程收据复核。`capture-receipt` 的 `--policy` 文件包含 `destination_chain_id`、`accepted_genesis`、十进制字符串 `minimum_confirmations`（至少 `6`）和 64 位十六进制 `minimum_inclusion_work`；阈值必须来自接收方明确政策，不能让发送方单方面降低。

## 失败与完成门槛

源或目的分叉导致同步页公共祖先变化时，此工具拒绝继续该页；操作人应重新从双方已验证共同祖先取完整历史并保留旧分叉证据。缺页、错误顺序或目的源视图过期使节点拒绝导入或收据。互相矛盾的终局证书必须暂停相关价值操作并保全两份证据。队列满时停止接收和记录容量事件，不自动清理和退款。唯一出口 ID 使重新投递不会产生第二份目的价值，但重复提交可能继续消耗网络与存储资源。

`python3 -m unittest discover -s tools -p test_interstellar_transfer.py -v` 只验证封装、篡改拒绝、落盘重复、同步页门槛和节点拒绝路径。它不是两区真实服务演练。F 完成还需正式创世下的断联/乱序/重启/深重组/矛盾证书及签名锁演练、返程历史的独立重放和长途保管容量证据。G 完成另需独立所有者、外部复核和物理远方路由证据。

正式 Earth 创世上的一次[本地返程历史重放](../../../../2026-09-28/docs/operations/EARTH_RETURN_REPLAY.md)已保存 101 页、202 个目的区块及成熟回执的持久转交和重启复核证据。源区副本仍在线，同机文件接触不能代替上文的远方部署和物理链路门槛。


2026-09-28 的[隔离真实节点演练](../../../../2026-09-28/docs/research/evidence/contact-drill-20260928.json)新增了正式创世下前向乱序拒绝、接触中断与重启、重复导入拒绝、双向历史重放及归档恢复；源历史至 438，目的至 202。停掉本地源副本后目的余额 API 返回 503，恢复不含新远方数据的同一副本即可恢复 `source_fresh`。这不是远方起源新鲜度证明，详见[断联与存储提案](../../../../2026-09-28/docs/research/DISCONNECTION_AND_STORAGE_PROPOSAL.md)。队列边界现有 8 项测试，但物理路线与跨所有者条件保持未完成。


## 自动渐进发现与多跳承载

[接触 mesh 原型](INTERSTELLAR_NODE_MESH.md)可封装本工具的精确帧，在只知道相邻节点的三地区拓扑里逐步传播签名身份、寻找候选下一跳并持久转发。目的签名收件回执只证明该传输身份声明保存了证据；`apply` 的区域账本重放、签名终局、唯一导入、成熟验证仍必需。中间地区仅中继字节，不导入/发行。无价值通用 fixture 普通启动现包括签名 IPv4 TCP 地面适配，实际本机套接字多跳/重试与原生导入已检查；跨设备、加密/物理通信、长期密钥与独立资格仍未完成。
