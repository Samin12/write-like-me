#!/bin/zsh
# Render each page tall, then trim the empty background at the bottom.
cd "${0:A:h}"
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
pages=(${@:-story how compare formats echo results}); [[ $# -eq 0 ]] && pages=(story how compare formats echo results)
for p in $pages; do
  "$CH" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1.5 --window-size=1600,2400 --screenshot="$PWD/../$p.png" "file://$PWD/$p.html" >/dev/null 2>&1
  python3 -c '
import sys; from PIL import Image
im=Image.open(sys.argv[1]).convert("RGB"); w,h=im.size; px=im.load(); bg=px[2,h-2]
y=h-1
while y>0 and all(px[x,y]==bg for x in range(0,w,4)): y-=1
im.crop((0,0,w,min(h,y+84))).save(sys.argv[1],optimize=True)' "$PWD/../$p.png"
done
