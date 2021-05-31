srcdir=python/files
dstdir=python

N=1;
for i in "${srcdir}"/*; do
  [ "$((N--))" = 0 ] && break
  cp -t "${dstdir}" -- "$i"
done