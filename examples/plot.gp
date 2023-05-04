# ~\~ language=Gnuplot filename=examples/plot.gp
# ~\~ begin <<README.md|examples/plot.gp>>[init]
    # enter your plotting commands here
# ~\~ end
# ~\~ begin <<README.md|examples/plot.gp>>[1]
    set term svg background rgb 'white' size 700, 500
    sinc(r) = sin(pi*r) / (pi*r)
    set isosamples 50, 50
    set hidden3d
    set xrange [-4:4]
    set yrange [-4:4]
    set xyplane 0
    set title "Sinc function"
    splot sinc(sqrt(x**2 + y**2)) t'' lc rgb '#5533cc'
# ~\~ end
