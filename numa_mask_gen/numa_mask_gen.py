#!/usr/bin/env python3

import subprocess
import re

class CPU_Info:
    """Simple class to collect node information using `lscpu`.  If `lscpu` is not
       found, the class will exit with an exception"""
    def __init__(self):
        def __lscpu():
            """ __lscpu will read the information from `lscpu`, and place the
                data in a simple dict, with the key being the part before the
                ":" and the value all data after.
            """
            try:
                lscpu_cmd = 'lscpu'
                lscpu_out = subprocess.run(lscpu_cmd, stdout=subprocess.PIPE)
                lscpu_dict = {}

                for line in lscpu_out.stdout.splitlines():
                    key, value = line.split(b':')
                    lscpu_dict[key.strip()] = value.strip()
            except Exception as err:
                print(f"ERROR: Error running '{lscpu_cmd}'. ({err.args[1]})")
                lscpu_dict = None
            finally:
                return lscpu_dict

        def __str2range(str):
            """ Take a string with both commas and numberic ranges (e.g., n-m)
            and convert to a list with the n-m range expanded.  The range
            will be inclusive.  That is 2-3 will return [2,3].
            """
            ranges_in = str.split(b',')
            ranges = []
            for r in ranges_in:
                lr = list(map(int, r.split(b'-')))
                ranges.extend([*range(lr[0], lr[-1]+1)])
            return ranges

        lscpu = __lscpu()
        if lscpu is not None:
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
            self.Error = False
        else:
            self.Error = True
