# numa_mask_gen

Generate a CPU Mask list usable by MPI-based jobs run with Slurm's `srun`, or
`mpirun` from any of the MPI libraries (e.g., [mpich](https://www.mpich.org/),
[openMPI](https://www.open-mpi.org/)).

*numa_mask_gen* can either poll the node (using [`lscpu`](https://man7.org/linux/man-pages/man1/lscpu.1.html))
or with user supplied values using the `--sockets`, `--cores-per-socket`, and
`--numa-nodes` command line options, where `--sockets` is the number of sockets on
the node, `--cores-per-socket` are the number of physical cores per CPU, and
`--numa-nodes` are the number of NUMA zones per node.  

If using a hybrid MPI+openMP executable, supply the number of threads using the
`--threads` option.

By default, *numa_mask_gen* will attempt to use the hyperthreaded (virtual)
cores.  The assumption is the hyperthreaded cores are numbered n through n*2-1
where n is the number of physical cores per node.

*numa_mask_gen* will print the hex prepresentation of the mask, unless both
`--no-hyperthreads` and `--cpu-list` options are given.  Note, a digital list
of CPUs is not possible when using hyperthreads.
