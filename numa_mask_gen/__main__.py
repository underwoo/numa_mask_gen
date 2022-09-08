def main():
    import argparse
    import sys

    arg_parser = argparse.ArgumentParser(description='Generate a CPU mask for MPI processor pinning')
    arg_parser.add_argument('--threads',
                            metavar='OMP_THREADS',
                            type=int,
                            help="Number of OpenMP threads (default: %(default)s)",
                            default=1)
    arg_parser.add_argument('--sockets',
                            metavar='NUM_SOCKETS',
                            type=int,
                            help="Number of sockets per node",
                            default=-1)
    arg_parser.add_argument('--cores-per-socket',
                            metavar='CORES_PER_SOCKET',
                            type=int,
                            help="Number of cores per socket",
                            default=-1)
    arg_parser.add_argument('--numa-nodes',
                            metavar='NUM_NUMA_NODES',
                            type=int,
                            help="Number of NUMA Memory zzones",
                            default=-1)
    arg_parser.add_argument('--use-lscpu',
                            action='store_true',
                            help="Use the `lscpu` command to determine system information.  Any value "
                            "given to all but `--threads` will be ignored. (default: %(default)s)")
    arg_parser.add_argument('--verbose','-v',
                            action='count',
                            help="Be verbose in the output",
                            default=0)
    arg_parser.add_argument('--no-hyperthreads',
                            action='store_true',
                            default=False,
                            help="Indicate if the mask should not include the core's hyperthread "
                                 "(default: %(default)s)")
    arg_parser.add_argument('--cpu-list',
                            action='store_true',
                            default=False,
                            help="Indicate if a CPU ID list should be printed, instead of a hex mask "
                                 "If using hyperthreads, then this option will be ignored. "
                                 "(default: %(default)s)")
    args = arg_parser.parse_args()

    if not args.no_hyperthreads and args.cpu_list:
        print("Ignoring `--cpu-list` since using hyperthreads.", file=sys.stderr)

    sockets = -1
    cores_per_socket = -1
    memZones = -1
    threads = args.threads
    totCores = -1

    if args.use_lscpu:
        cpu_info = CPU_Info()
        if cpu_info.Error:
            print("Unable to gather node CPU and Memory information.  Please try again "
                  "using options `--sockets`, `--cores-per-socet` and `--numa-nodes`.",
                  file=sys.stderr)
            sys.exit(1)

        if args.verbose >= 2:
            print(f'architecture {cpu_info.architecture}', file=sys.stderr)
            print(f'cpu_opmodes {cpu_info.cpu_opmodes}', file=sys.stderr)
            print(f'byte_order {cpu_info.byte_order}', file=sys.stderr)
            print(f'address_sizes {cpu_info.address_sizes}', file=sys.stderr)
            print(f'cpus {cpu_info.cpus}', file=sys.stderr)
            print(f'cpus_online {cpu_info.cpus_online}', file=sys.stderr)
            print(f'num_core_threads {cpu_info.num_core_threads}', file=sys.stderr)
            print(f'cores_per_socket {cpu_info.cores_per_socket}', file=sys.stderr)
            print(f'sockets {cpu_info.sockets}', file=sys.stderr)
            print(f'numa_nodes {cpu_info.numa_nodes}', file=sys.stderr)
            print(f'vendor_id {cpu_info.vendor_id}', file=sys.stderr)
            print(f'cpu_family {cpu_info.cpu_family}', file=sys.stderr)
            print(f'model {cpu_info.model}', file=sys.stderr)
            print(f'model_name {cpu_info.model_name}', file=sys.stderr)
            print(f'stepping {cpu_info.stepping}', file=sys.stderr)
            print(f'cpu_MHz {cpu_info.cpu_MHz}', file=sys.stderr)
            print(f'cpu_MHz_max {cpu_info.cpu_MHz_max}', file=sys.stderr)
            print(f'cpu_MHz_min {cpu_info.cpu_MHz_min}', file=sys.stderr)
            print(f'bogoMIPS {cpu_info.bogoMIPS}', file=sys.stderr)
            print(f'virtualization {cpu_info.virtualization}', file=sys.stderr)
            print(f'l1d_cache {cpu_info.l1d_cache}', file=sys.stderr)
            print(f'l1i_cache {cpu_info.l1i_cache}', file=sys.stderr)
            print(f'l2_cache {cpu_info.l2_cache}', file=sys.stderr)
            print(f'l3_cache {cpu_info.l3_cache}', file=sys.stderr)
            print(f'cpus_numa_nodes {cpu_info.cpus_numa_nodes}', file=sys.stderr)
            print(f'flags {cpu_info.flags}', file=sys.stderr)

        sockets = cpu_info.sockets
        cores_per_socket = cpu_info.cores_per_socket
        memZones = cpu_info.numa_nodes
    else:
        # check if any value was not given
        if any(flag <= 0 for flag in [args.sockets, args.cores_per_socket, args.numa_nodes]):
            print(f"Must supply positive integers for `--sockets`, `--cores-per-socket`, and `--numa-nodes`.",
                  file=sys.stderr)
            print(f"Received:\n    sockets = {args.sockets}", file=sys.stderr)
            print(f"    cores-per-socket = {args.cores_per_socket}", file=sys.stderr)
            print(f"    numa-nodes = {args.numa_nodes}", file=sys.stderr)
            sys.exit(1)

        else:
            sockets = args.sockets
            cores_per_socket = args.cores_per_socket
            memZones = args.numa_nodes

    # Calculated values
    totCores = sockets * cores_per_socket
    cores_in_numa_node = int(totCores / memZones)

    if args.verbose >= 1:
        print(f"Using settings", file=sys.stderr)
        print(f"    sockets = {sockets}", file=sys.stderr)
        print(f"    cores-per-socket = {cores_per_socket}", file=sys.stderr)
        print(f"    numa-nodes = {memZones}", file=sys.stderr)
        print(f"    Total Physical Cores = {totCores}", file=sys.stderr)
        print(f"    Cores in NUMA Zones = {cores_in_numa_node}", file=sys.stderr)
        print(f"    OMP threads = {threads}", file=sys.stderr)

    cpu_list = [i + j * cores_in_numa_node \
                for i in range(0, cores_in_numa_node, threads) \
                for j in range(0, memZones)]

    if args.verbose >=2:
        print(f"CPU List: {','.join((str(n) for n in cpu_list))}", file=sys.stderr)

    # Width of hex string representation of core mask for node with totCores
    hex_width = int(totCores / 4) if totCores >=4 else 1

    if not args.no_hyperthreads and not args.cpu_list:
        print(','.join((f"{2**n:#0x}{2**n:0{hex_width}x}" for n in cpu_list)))
    elif args.no_hyperthreads and not args.cpu_list:
        print(','.join((f"{2**n:#0x}" for n in cpu_list)))
    else:
        print(','.join((str(n) for n in cpu_list)))

if __name__ == "__main__":
    main()
