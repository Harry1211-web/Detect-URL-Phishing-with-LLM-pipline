#!/bin/sh
# Exports a .docx to PDF with real Times New Roman; Liberation Serif breaks Vietnamese glyphs.
# Usage: render_pdf.sh <dir holding p.docx>. Needs: docker build -t paper-render . (run in this folder)
W="$1"; mkdir -p "$W/fonts"; cp /c/Windows/Fonts/times*.ttf "$W/fonts/"
MSYS_NO_PATHCONV=1 docker run --rm -v "$(cygpath -w "$W"):/w" -w /w paper-render sh -c \
  'mkdir -p /tmp/.fonts; cp fonts/* /tmp/.fonts/; HOME=/tmp fc-cache -f; HOME=/tmp soffice --headless --convert-to pdf p.docx >/dev/null 2>&1; pdfinfo p.pdf | grep Pages'
