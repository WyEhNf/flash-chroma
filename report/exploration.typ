#let navy = rgb("172b4d")
#let blue = rgb("2869a6")
#import "helpers.typ": meta

#set page(
  paper: "a4",
  margin: (top: 19mm, bottom: 18mm, left: 20mm, right: 18mm),
  numbering: "1",
  footer: context [#h(1fr)#text(size: 8pt, fill: gray)[极速焕彩 · 探索报告 ｜ #counter(page).display()]],
)
#set text(font: "Noto Sans CJK SC", size: 9.5pt, lang: "zh", region: "CN")
#set par(justify: true, leading: 0.68em)
#set heading(numbering: "1.1")
#set table(inset: 3pt, stroke: 0.3pt + rgb("b8c5d3"))
#show heading.where(level: 1): set text(size: 16pt, weight: "bold", fill: navy)
#show heading.where(level: 2): set text(size: 12pt, weight: "bold", fill: blue)

#align(center)[
  #v(30mm)
  #text(size: 26pt, weight: "bold", fill: navy)[极速焕彩]

  #v(6mm)
  #text(size: 17pt, fill: blue)[从题面拆解到可移植 SIMD 的完整探索报告]

  #v(18mm)
  #text(size: 12pt)[2026 Hackathon 决赛 · 第 16 题]

  #v(7mm)
  #text(size: 10pt)[三名本科生团队 · 18 天备赛 · 24 小时正式赛程]

  #v(18mm)
  #line(length: 60%, stroke: 1pt + blue)

  #v(9mm)
  #text(size: 10pt)[基于 #meta.run_count 份独立运行记录、#meta.candidate_count 个当前候选、#meta.image_row_count 条逐图统计]

  #v(4mm)
  #text(size: 9pt)[报告数据基准 Git：#meta.source_git_commit]

  #v(31mm)
  #text(size: 9pt, fill: gray)[工作目录：\~/problem_probe/16 ｜ 报告源文件：report/exploration.typ]
]

#pagebreak()
#outline(title: [目录], depth: 2)
#pagebreak()

#include "chapters/01_problem_method.typ"
#include "chapters/02_engineering.typ"
#include "chapters/03_exploration.typ"
#include "chapters/04_results_decision.typ"
#include "chapters/05_user_guide.typ"
#include "chapters/06_appendices.typ"
