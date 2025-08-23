def neighbors4(y, x, H, W):
    if y>0: yield (y-1, x)
    if y+1<H: yield (y+1, x)
    if x>0: yield (y, x-1)
    if x+1<W: yield (y, x+1)
