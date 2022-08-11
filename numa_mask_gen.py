#!/usr/bin/env python3

import subprocess
import re

class CPU_Info:
    def __init__(self):
        def __lscpu():
            lscpu_cmd = 'lscpu'
            lscpu_out = subprocess.run(lscpu_cmd, stdout=subprocess.PIPE)
            lscpu_dict = {}

            for line in lscpu_out.stdout.splitlines():
                key, value = line.split(b':')
                lscpu_dict[key.strip()] = value.strip()
            return lscpu_dict

        def __str2range(str):
            ranges_in = str.split(b',')
            ranges = []
            for r in ranges_in:
                lr = list(map(int, r.split(b'-')))
                ranges.extend([*range(lr[0], lr[-1]+1)])
            return ranges
        lscpu = __lscpu()

        self.architecture = lscpu[b'Architecture']
        self.cpu_opmodes = lscpu[b'CPU op-mode(s)']
        self.byte_order = lscpu[b'Byte Order']
        self.address_sizes = lscpu[b'Address sizes']
        self.cpus = int(lscpu[b'CPU(s)'])
        self.cpus_online = __str2range(lscpu[b'On-line CPU(s) list'])
        self.num_core_threads = int(lscpu[b'Thread(s) per core'])
        self.cores_per_socket = int(lscpu[b'Core(s) per socket'])
        self.sockets = int(lscpu[b'Socket(s)'])
        self.numa_nodes = int(lscpu[b'NUMA node(s)'])
        self.vendor_id = lscpu[b'Vendor ID']
        self.cpu_family = lscpu[b'CPU family']
        self.model = lscpu[b'Model']
        self.model_name = lscpu[b'Model name']
        self.stepping = lscpu[b'Stepping']
        self.cpu_MHz = float(lscpu[b'CPU MHz'])
        self.cpu_MHz_max = float(lscpu[b'CPU max MHz'])
        self.cpu_MHz_min = float(lscpu[b'CPU min MHz'])
        self.bogoMIPS = float(lscpu[b'BogoMIPS'])
        self.virtualization = lscpu[b'Virtualization']
        self.l1d_cache = lscpu[b'L1d cache']
        self.l1i_cache = lscpu[b'L1i cache']
        self.l2_cache = lscpu[b'L2 cache']
        self.l3_cache = lscpu[b'L3 cache']
        self.cpus_numa_nodes = []
        for numa_node in sorted([key for key in lscpu.keys() if re.match(b'NUMA node\d+ CPU\(s\)', key)]):
            self.cpus_numa_nodes.append(__str2range(lscpu[numa_node]))
        self.flags = lscpu[b'Flags'].split()


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
                            help="",
                            default=0)
                        
    args = arg_parser.parse_args()

    sockets = -1
    cores_per_socket = -1
    memZones = -1
    threads = args.threads
    totCores = -1

    if args.use_lscpu:
        cpu_info = CPU_Info()

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

    totCores = sockets * cores_per_socket

    if args.verbose >= 1:
        print(f"Using settings", file=sys.stderr)
        print(f"    sockets = {sockets}", file=sys.stderr)
        print(f"    cores-per-socket = {cores_per_socket}", file=sys.stderr)
        print(f"    numa-nodes = {memZones}", file=sys.stderr)
        print(f"    Total Physical Cores = {totCores}", file=sys.stderr)
        print(f"    OMP threads = {threads}", file=sys.stderr)
        
    
if __name__ == "__main__":
    main()