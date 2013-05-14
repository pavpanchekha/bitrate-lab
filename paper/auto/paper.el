(TeX-add-style-hook "paper"
 (lambda ()
    (LaTeX-add-bibliographies)
    (TeX-run-style-hooks
     "usenix"
     "graphicx"
     "epsfig"
     ""
     "latex2e"
     "art10"
     "article"
     "10pt"
     "twocolumn"
     "letterpaper")))

