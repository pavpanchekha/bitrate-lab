run() {
    pypy harness.py "$1" ../data/"$2".dat /tmp/log | tee ../out/"$1"_"$2".out
    python draw_trace.py ../data/"$2".dat /tmp/log
}
