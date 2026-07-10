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
