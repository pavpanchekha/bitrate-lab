(TeX-add-style-hook "paper"
 (lambda ()
    (LaTeX-add-bibliographies)
    (LaTeX-add-labels
     "tbl:bitrates"
     "sec:samplerate"
     "sec:minstrel"
     "table:mrr"
     "sec:methodology"
     "figure:1"
     "sec:analysis"
     "figure:2"
     "figure:3"
     "sec:minproved"
     "table:2"
     "figure:4"
     "sec:availability"
     "sec:future-work"
     "sec:conclusion"
     "sec:acknowledgments")
    (TeX-run-style-hooks
     "hyperref"
     "subcaption"
     "graphicx"
     ""
     "geometry"
     "margin=1in"
     "latex2e"
     "art10"
     "article"
     "10pt"
     "twocolumn")))

