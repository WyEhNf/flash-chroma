#let meta = json("generated/meta.json")

#let csvtable(path, widths, size: 7pt, inset: 3pt) = {
  let rows = csv(path)
  text(size: size)[
    #table(
      columns: widths,
      inset: inset,
      table.header(..rows.at(0).map(cell => [#strong(cell)])),
      ..rows.slice(1).map(row => row.map(cell => [#cell])).flatten(),
    )
  ]
}
