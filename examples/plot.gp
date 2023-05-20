# ~/~ begin <<docs/index.md#examples/plot.gp>>[init]
set term svg background rgb 'white' size 700, 500
sinc(r) = sin(pi*r) / (pi*r)
set isosamples 50, 50
set hidden3d
set xrange [-4:4]
set yrange [-4:4]
set xyplane 0
set title "Sinc function"
splot sinc(sqrt(x**2 + y**2)) t'' lc rgb '#5533cc'
# ~/~ end