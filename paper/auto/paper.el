(TeX-add-style-hook "paper"
 (lambda ()
    (LaTeX-add-bibliographies
     "../common/bibliography")
    (TeX-run-style-hooks
     "endnotes"
     "epsfig"
     "usenix"
     ""
     "latex2e"
     "art10"
     "article"
     "10pt"
     "twocolumn"
     "letterpaper")))

