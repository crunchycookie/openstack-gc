import sys
import time

import pandas as pd
from math_utils import pick_random
from external import dispatch

# 1 - normalized azure trace csv
# 2 - starting time
# 3 - end time
# 4 - max number of requests at a time
# 5 - max lifetime of a vm
# 6 - max vcpu of an instant

# Example:
# python3 trace-generator.py 4-min-test/nrl_azure_packing_2020.csv 0.819502315018326 0.8208333 5 0.00277778 12
# csv file is generated for 4 minutes (0.00277778 days) between 0.819502315018326 and 0.8208333. max req. set to 5 and
# max lifetime is the duration of experiment.

nrl_trace_file = sys.argv[1]
t_start = float(sys.argv[2])
t_stop = float(sys.argv[3])

max_rq_cnt = float(sys.argv[4])
max_lft = float(sys.argv[5])
max_vcpu_cnt = float(sys.argv[6])

print("nrl_trace_file: ", nrl_trace_file, " t_start: ", t_start, " t_stop: ", t_stop, " max_rq_cnt: ", max_rq_cnt,
      "max_lft: ", max_lft, "max_vcpu_cnt: ", max_vcpu_cnt)

df = pd.read_csv(nrl_trace_file)
df = df[t_start <= df['time']]
df = df[df['time'] <= t_stop]


def generate_rqs(rq_count, row, time, type, bucket):
    for rq in range(rq_count):
        lifetime = pick_random(dst=eval(row['lifetime_distribution'][0])) * max_lft
        vcpu = round(pick_random(dst=eval(row['vcpu_distribution'][0])) * max_vcpu_cnt)
        if vcpu > 0:
            bucket.append({
                'name': 'VM-' + str(time) + '-' + type + '-' + str(rq),
                'type': type,
                'lifetime': lifetime,
                'vcpu': vcpu
            })


t_s = df['time'].values
for idx, t in enumerate(t_s):
    row = df.loc[df['time'] == t].to_dict('list')

    vm_rqs = []
    total_rq_cnt = row['request_count'][0] * max_rq_cnt
    reg_rq_cnt = round(total_rq_cnt * row['regular_vm_count'][0])
    evct_rq_cnt = round(total_rq_cnt * row['evictable_vm_count'][0])
    if reg_rq_cnt > 0:
        generate_rqs(rq_count=reg_rq_cnt, row=row, time=t, type='regular', bucket=vm_rqs)
    if evct_rq_cnt > 0:
        generate_rqs(rq_count=evct_rq_cnt, row=row, time=t, type='evictable', bucket=vm_rqs)

    dispatch(vm_rqs=vm_rqs)

    if (idx + 1) < len(t_s):
        t_to = t_s[idx + 1] - t
        wait_for = t_to * (24 * 3600)
        print("time: ", t, "total requested: ", len(vm_rqs), "waiting for: ", wait_for)
        time.sleep(wait_for)