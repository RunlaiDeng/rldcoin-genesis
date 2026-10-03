# 星际中继节点：启动、渐进发现和三地区地面验收

这项工作落实[节点中继要求](../research/INTERSTELLAR_NODE_MESH_REQUIREMENTS.md)。程序是共识源码承诺之外的地面传输原型；节点地区标签是自报元数据，没有签署创世、发币或付款权限。当前仅测试网运行，新主网尚未上线。

## 复现自动发现与断联恢复

需要 Python 3.11 或更新版本及 `tools/interstellar-mesh-requirements.txt` 指定依赖。新建专用虚拟环境并安装依赖，然后运行：

```sh
python3 -m venv /absolute/private-mesh-venv
/absolute/private-mesh-venv/bin/python -m pip install -r tools/interstellar-mesh-requirements.txt
/absolute/private-mesh-venv/bin/python -m unittest discover -s tools -p 'test_interstellar_*.py' -v
/absolute/private-mesh-venv/bin/python tools/interstellar_mesh_drill.py --output /absolute/new-mesh-drill.json
```

该演练启动三个真实本机常驻进程，逻辑标签为地球、比邻星、仙女座；仅地球↔比邻星、比邻星↔仙女座两个相邻目录接触。它检查每个进程自动学到三个节点、地球通过比邻星找出仙女座路径，中继停机时消息保留、发送端重启保留队列、中继恢复后原样传递、签名收件回执返回，以及目的端重启。临时目录含测试身份私钥，退出后清理；报告只含非敏感结果。

2026-09-30：16 项 mesh 检查加原传输/路由预算共 34 项通过；三进程演练 PASS。[报告](../../../mesh/docs/operations/evidence/interstellar-mesh-20260930.json)记录两跳证据转发与回程。这不是三个星系部署，未演练账本导入、真实光时、长期密钥、独立运营或主网上线。

## 启动自己的传输节点

先确定本叠加网共同的 64 位十六进制网络标识，以及本节点的地区标识。每个地区可以有多个不同节点。共识链的真实身份仍另行固定，不由这些传输标识决定。

```sh
python3 tools/interstellar_mesh.py init --state /absolute/private/earth-mesh --network NETWORK_HEX --region REGION_HEX --label earth
```

输出只有公共身份。`identity.private.json` 是传输节点私钥，不能上传；不要复用钱包或终局密钥。路径须绝对且不经过符号链接，macOS 临时目录使用其 `/private/...` 真实路径。一次 init 后继续用同一目录；不重新生成身份。

为相邻端交换并独立核对 `node_id`，为每个方向准备独立目录，配置文件为规范 JSON（键排序、无空白、无重复键）：

```json
{"contacts":[{"inbox":"/absolute/contact/proxima-to-earth","outbox":"/absolute/contact/earth-to-proxima","peer":"PINNED_PROXIMA_NODE_HEX"}],"format":"RLD-CONTACT-MESH-V1","network":"NETWORK_HEX","state":"/absolute/private/earth-mesh"}
```

对端以自身身份配置对应方向。地面同机演练将一端 outbox 对接另一端 inbox；真实运输适配器必须复制**完整原样**的交换文件（文件名为内容哈希），先写临时文件再持久原子提交到 inbox。适配器可以在未来映射到 BPv7、无线/激光接触或物理携带；本原型没有这些物理服务。HTTP/TCP 的地面超时不能被当作跨星际往返上限。

```sh
python3 tools/interstellar_mesh.py run --config /absolute/private/earth.config.json
python3 tools/interstellar_mesh.py status --config /absolute/private/earth.config.json
python3 tools/interstellar_mesh.py enqueue --config /absolute/private/earth.config.json --destination-node DESTINATION_NODE_HEX --frame /absolute/evidence.frame.json
python3 tools/interstellar_mesh.py export-received --config /absolute/private/destination.config.json --packet-id PACKET_HEX --output /absolute/received.frame.json
```

`run` 常驻轮询接触目录，自动传播签名通告、学习远端候选路线和继续队列；Ctrl-C 可停止并保留状态。重新启动同一配置会恢复。可以与已验收的区域账本节点在同一主机旁运行，已采用节点仍不默认启用；通用无价值 fixture 节点现通过同一普通启动流程启用此运行时，详见[候选启动方式](../../tools/regional-ledger/README.md)。测试网的原有 run.py、签名规则和固定源码保持不变。

目的端输出帧后，还须按[证据运输操作](INTERSTELLAR_EVIDENCE_TRANSPORT.md)交给固定身份的区域节点独立验证。`EVIDENCE_STORED_NOT_LEDGER_ACCEPTED` 仅指目的传输节点声明持久收件；`payment_authorized` 和 `physical_route_verified` 恒为 false。没有路由、无回程、收件失败、队列满和失联均不能退款或更改资产。

## 运行边界和后续验收

通用无价值 fixture 的普通节点启动还包括 `interstellar_tcp.py` IPv4 适配；默认只监听本机临时端口，显式 `--mesh-listen IPv4:PORT` 可固定端点。相邻配置可以用 `{"peer":"PINNED_NODE_HEX","host":"127.0.0.1","port":39001}`，必须双方独立核对身份。这里只允许运营者配置的字面 IPv4/整数端口；签名通告不提供可执行远程 URL。独立 `interstellar_mesh.py run` 仍仅处理目录，TCP 由普通原生 fixture 生命周期启用，详见[使用与复现](../../tools/regional-ledger/README.md)。

TCP 请求和回复绑定指定身份、网络、随机 nonce 和精确交换哈希；整份交换持久提交后才确认保管。原始证据始终保留，回复丢失、重连和重复不会产生信用；原生 Rust 另行验收。两个入站线程、每轮四个出站邻居、20 MiB 内层交换和三秒地面接入等待均为资源限额，不能解释成星际时延或退款条件。套接字等待不占 mesh 锁，队列发送轮换位置持久保存。接触历史是本进程的本地观测。

13 项实际套接字检查覆盖双跳、备用路径、断线/重启、确认丢失、同时双向接触、拒收/写失败/恶意输入和多批轮换；原 35 项运输检查保持通过。三原生进程的[实际 TCP 价值演练](evidence/regional-native-tcp-campaign-20260930.json)不使用共享运输目录，并在地球失联期间完成远端付款/再出口。这仅为同机 loopback、双向、验签但未加密的地面适配；跨设备、独立所有者、加密、单向/无线/BPv7、真实时延/容量计划和物理路线均未资格化。

通告有单调序号和签名。旧通告不能替代新的；同序号矛盾签名交换被拒绝并保留原始 inbox 文件。远方通告只是候选路线；失联不按本地几秒超时删除，状态时间只是本地观测。私钥和状态备份回滚、撤销/轮换、长时密码安全、对抗隔离与真正自动本地发现还需资格工作。

节点保留原始消息直到容量上限；接触消费仅删除已持久处理的**交换文件**，不会删除消息证据。容量、错误文件和符号链接拒收时保留证据。已认证恶意邻居仍可能黑洞、谎报接触或耗尽限额；签名不证明其可用性，限额也不证明抗 Sybil。

后续正式适配须证明前向及返向接触容量、负载恢复、时延计划、持久保管、双所有者认证、故障与安全流程；区域目的节点长期离线政策和任意地区价值转移须另行验收。在这些条件落实前，官网只称“自动中继地面原型”，不称星际服务已上线。
