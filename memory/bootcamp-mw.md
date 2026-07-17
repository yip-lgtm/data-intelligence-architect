# MW01 Class I 項目清單

Daily cron 抽樣源。本檔案原本於 2026-07-02 workspace wipe 後遺失；本日（2026-07-06）重建。

## Class I 抽樣池（58 個項目）

MWTGe text 索引能直接查到嘅項目（已對 mwtge_lookup.py）：1.1, 1.3, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.13, 1.14, 1.15, 1.16, 1.18, 1.19, 1.20, 1.21, 1.22, 1.23, 1.24, 1.26, 1.27, 1.28, 1.29, 1.30, 1.31, 1.32, 1.36, 1.37, 1.38, 1.39, 1.40。

MWTGe text 索引未覆蓋／字面唔match嘅項目（random 會跳過，輸出會標明 fallback）：1.2, 1.4, 1.12, 1.17, 1.25, 1.33, 1.34, 1.35, 1.41, 1.42, 1.43, 1.44, 1.45, 1.46, 1.47, 1.48, 1.49, 1.50, 1.51, 1.52, 1.53, 1.54, 1.55, 1.56, 1.57, 1.58, 1.59, 1.60, 1.61, 1.62。

完整 Class I 列表（用戶 cron 提供）：

```
1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10,
1.11, 1.12, 1.14, 1.15, 1.16, 1.17, 1.20, 1.21, 1.22, 1.23,
1.24, 1.25, 1.26, 1.27, 1.28, 1.30, 1.31, 1.32, 1.33, 1.34,
1.35, 1.36, 1.37, 1.38, 1.39, 1.40, 1.41, 1.42, 1.43, 1.44,
1.45, 1.46, 1.47, 1.48, 1.49, 1.50, 1.51, 1.52, 1.53, 1.54,
1.55, 1.56, 1.57, 1.58, 1.59, 1.60, 1.61, 1.62
```

## 抽樣方法

`random.seed(datetime.utcnow().toordinal())` → `random.choice(items)`，
從「用戶列表 ∩ MWTGe 索引」交集抽；抽唔到 → fallback 去最接近 hit，否則報錯請人手 pick。

## 每日抽樣記錄

| 日期 (UTC) | 抽中 | MWTGe 頁碼 | 備註 |
|---|---|---|---|
| 2026-07-06 | 1.31 | 104 | 內牆板 metal dowel；height > 10m |
| 2026-07-07 | 1.31 | 18–19, 104, 174–175 | 同項目兩日連中（seed=739803/739804 都指 1.31）；description pages 18-19、schedule page 104、Appendix VII 圖則（2.33 family）pages 174-175 |
| 2026-07-08 | 1.6 | 32–33, 61, 103, 113 | Protective Barrier（Class I）— random seed=739805 picked 1.6；description + flowcharts pp.32-33、comparison with 2.5 p.61、schedule p.103、Form MW01 p.113；**Class I 冇 Appendix VII 典型圖則**（Appendix VII 只覆蓋 Class II/III per §4.2.11） |
| 2026-07-09 | 1.40 | 26, 69, 102, 105, 111, 113 | Removal of metal gate at fence wall / building entrance — random seed=739806 抽中 1.44（非 indexable），fallback 去最接近 indexable hit **1.40**；Section 3.10 描述 + Class I vs II/III 比較 p.26；提交資料（operating mode, height, weight of each leaf, locking devices）p.69；Class I schedule p.102；item 1.40 法定描述 p.105；Appendix III PRC 配對（RSC Demolition）p.111；Form MW01 p.113；同樣 **Class I 冇 Appendix VII 典型圖則** |
| 2026-07-10 | 1.8 | 21, 69, 71, 102, 103, 113 | External mesh fence（Class I，Type A）— random seed=739807 抽中 1.57（非 indexable），fallback 去索引內 hit **1.8**；Chapter 3.7 description p.21；其他提交資料表（fence wall 1.7-1.10：height, material & standards）p.69；Class I flowcharts（Notification / Submission / Completion）pp.65-66、Class I Simplified Requirements (§4.3) p.68；Appendix I Type 配對（1.8 → Class I / Type A）p.102；Appendix II 法定描述 p.103；Form MW01 p.113；同樣 **Class I 冇 Appendix VII 典型圖則** — closest analogues 為 item 2.7（external mesh fence，height ≤ 3m）Appendix VII pp.138-139 / PDF pp.174-175，同 sub-category 仲有 item 2.6（solid fence wall，height ≤ 1.5m）Appendix VII pp.136-137 / PDF pp.172-173 可參考 base detail。但呢兩份係 Class II 嘅典型設計，唔可以照搬作 Class I submission 嘅唯一依據 |
| 2026-07-11 | 1.37 | 35, 68, 69, 103, 113 | Removal of chimney attached to external wall / on roof（Class I）— random seed=739808 抽中 1.37（pool hit，無 fallback）；Chapter 3 「Removal of Chimney」 description p.35；Class I Simplified Requirements §4.3 pp.68 / s.30-32 B(MW)R；其他提交資料「Dimensions of the chimney」p.69；Appendix II 法定描述（items of MW）start p.103（1.37 喺 1.6–1.40 區段）；Appendix VII **唔覆蓋 Class I**（per §4.2.11，Appendix VII only Class II/III）— closest analogue 為 item 2.37 嘅 Appendix VII pp.144-145 / PDF pp.180-181（typical removal details for chimney ≤ 500 mm cross-section, ≤ 5m height）但係 Class II 圖則唔可以直接照搬；Form MW01 p.113 |
| 2026-07-12 | 1.36 | 15, 17, 18, 63, 64, 86, 100, 106, 107, 179 | Removal of any underground drain（Class I）— random seed=739809（ordinal of 2026-07-12）抽中 1.36（pool hit，無 fallback）；Chapter 3 「Drainage」 comparison table (1.25/1.36/1.26 vs 2.28/2.29/2.36) p.15；Chapter 3.4 「Excavation Works & Spread Footing」 p.17、Chapter 3.5 (Excavation associated with other MW) p.18；§4.3 「Simplified Requirements」Class I flowchart p.63；其他提交資料「Drainage – 1.25, 1.26 & 1.36: Size, material & standards」p.64；§10.9.5 Construction Site Safety (excavation fencing per CS(S)R reg.40) p.86；Schedule 1 Part 3 legal description item 1.36 p.100；Appendix III PRC matching（1.36 → RSC Demolition Works）p.106；Form MW01 sample p.107；Appendix VII **唔覆蓋 Class I** — closest analogue 為 item 2.36 嘅 Appendix VII PDF p.179（typical removal details of underground drain for Class II），但係 Class II 圖則唔可以照搬 |
| 2026-07-13 | 1.7 | 21, 68, 69, 102, 103, 111, 112, 172–175 | Erection or alteration of any solid fence wall, on-grade; height > 1.5 m & ≤ 5 m（Class I, Type A）— random seed=739810（ordinal of 2026-07-13）抽中 1.7（pool hit，無 fallback）；Chapter 3.7 「Fence Wall or External Mesh Fence」comparison table (1.7 vs 2.6 vs 1.8 vs 2.7) p.21 — 1.7 height band 1.5–5 m, on-grade, B(P)R 30 / APP-103 / ADV-22 / no effect on MOE·MOA·EVA；§4.3 「Simplified Requirements」Class I s.30-32 B(MW)R p.68；其他提交資料「Fence wall or external mesh fence — 1.7 to 1.10: Height, material & standards」p.69；Appendix I Type A 配對（1.7 → Class I / Type A）p.102；Appendix II 法定描述 item 1.7 p.103；Appendix III PRC matching — RGBC can carry all, 1.7 **NOT** on RSC Demolition Works list，RMWC(Co) for Type A applies p.111；Form MW01 sample p.112（form spec starts p.112）；Appendix VII **唔覆蓋 Class I** — closest analogues are item 2.6 (solid fence wall h ≤ 1.5 m) Appendix VII pp.136-137 / PDF pp.172-173 同 item 2.7 (external mesh fence h ≤ 3 m) Appendix VII pp.138-139 / PDF pp.174-175，but these are Class II drawings and CANNOT be copied as Class I submission |
| 2026-07-14 | 1.39 | 38, 40, 65, 67, 68, 102, 105, 111, 112, 130–131, 176–178, 181 | Removal of any unauthorized floor slab（Class I, Type A）— random seed=739811（ordinal of 2026-07-14）抽中 1.58（非 indexable in MWTGe text），fallback 去最接近 indexable unused hit **1.39**（pool 內 distance ≈ 0.19）；Chapter 3.16 「Removal of Unauthorized Floor Slab or Unauthorized Structure」第 3 個 simple comparison (1.39 vs 2.38) printed p.38 / PDF p.40；§4.2.11 「Appendix VII only Class II & III」printed p.65 / PDF p.67；§4.2.12 photos before/after 同 location 同 angle printed p.65 / PDF p.67；§4.3 「Simplified Requirements」Class I s.30-32 B(MW)R printed p.68 / PDF p.70；其他提交資料表 printed p.67 / PDF p.69 — 1.39 **唔列喺度**，standard Form MW01 package 已足夠；Appendix I Type A 配對（1.39 → Class I / Type A）printed p.102 / PDF p.104；Appendix II 法定描述 item 1.39 簡單一句「Removal of any unauthorized floor slab.」（**冇 explicit provisos**）printed p.105 / PDF p.107；Appendix III PRC matching printed p.111 / PDF p.113 — 1.39 明確列喺 **RSC (Demolition Works)** list（連同 1.5, 1.9, 1.10, 1.24, 1.30, 1.32, 1.33, 1.34, 1.36, 1.37, 1.38, 1.40），eligible PRC 限於 **RGBC** 或 **RSC(Demolition Works)**，**RMWC(Co) Type A Class I 唔包 1.39**；Form MW01 sample Appendix V printed p.112 / PDF p.114；Appendix VII **唔覆蓋 Class I** — closest analogue 為 item 2.38 (Removal of unauthorized structure hung under balcony/canopy soffit) Appendix VII printed p.181 / PDF p.183（直接同 1.39 喺 Chapter 3.16 third comparison 配對），其他 floor-slab related 仲有 item 2.1 (Formation of opening in slab) Appendix VII printed pp.130-131 / PDF pp.132-133 及 item 2.35 (Reinstatement of slab opening) Appendix VII printed pp.176-178 / PDF pp.178-180 — 全部 Class II 圖則 CANNOT 照搬作 Class I submission；Other considerations per Chapter 3.16: B(DW)R 10 not overload floor、B(DW)R 11 防突然倒塌切鋼筋、PNAP APP-21 公眾安全、Guidelines for Removal of Typical UBW s.4 — 雖然 1.39 法定描述冇 explicit geometric threshold，但實務必須 check cantilevered slab implications 同 load redistribution |
