import matplotlib.pyplot as plt


def parse_vm_latency_stats(name, raw_d):
    rt = raw_d['rteval']['Measurements']['Profile']['cyclictest']['system']['statistics']

    hst_raw = raw_d['rteval']['Measurements']['Profile']['cyclictest']['system']['histogram']
    hst = {}
    for e in hst_raw['bucket']:
        hst[int(e['@index'])] = int(e['@value'])
    return {
        'name': name,
        'min': float(rt['minimum']['#text']),
        'max': float(rt['maximum']['#text']),
        'median': float(rt['median']['#text']),
        'mode': float(rt['mode']['#text']),
        'range': float(rt['range']['#text']),
        'mean': float(rt['mean']['#text']),
        'mad': float(rt['mean_absolute_deviation']['#text']),
        'sd': float(rt['standard_deviation']['#text']),
        'hst': hst
    }


def visualize(data, title, x_lbl, y_lbl, out_plot_path, type):
    names = [e['name'] for e in data]
    mean = [e['mean'] for e in data]
    mad = [e['mad'] for e in data]

    if type == 'eb':
        fig, ax = plt.subplots()
        bars = ax.bar(names, mean, edgecolor="black")

        # Add error bars
        plt.errorbar(names, mean, yerr=mad, capsize=3, fmt="r--o", ecolor="black")

        # Annotate each bar with the mean value
        for bar, value in zip(bars, mean):
            height = bar.get_height()
            ax.text(bar.get_x() + (bar.get_width() * 0.8), height, f'{value:.2f}', ha='center', va='bottom')

    plt.title(title)
    plt.ylabel(y_lbl)
    plt.xlabel(x_lbl)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_plot_path, bbox_inches='tight')


def anlz_isolated(isolated_data):
    data = [
        parse_vm_latency_stats(name='pins_\npcpus_2', raw_d=isolated_data['PIN_1']),
        parse_vm_latency_stats(name='floats_\npcpus_1', raw_d=isolated_data['FLT_1']),
        parse_vm_latency_stats(name='floats_\npcpus_2', raw_d=isolated_data['FLT_2']),
        parse_vm_latency_stats(name='floats_\npcpus_3', raw_d=isolated_data['FLT_3']),
        parse_vm_latency_stats(name='floats_\npcpus_4', raw_d=isolated_data['FLT_4']),
    ]
    visualize(data=data, x_lbl="VM (vcpus=2) Core Affinity", y_lbl="Mean Latency ("r'$\mu$'"s)",
              title="Real-Time Performance vs Core Affinity", out_plot_path="results/rt-vs-core-affinity.svg", type='eb')


def anlz_dynamic(dynamic_data):
    data = [
        parse_vm_latency_stats(name='stable_vm\npcpus_6', raw_d=dynamic_data['PIN']),
        parse_vm_latency_stats(name='shrinking_hvm\npcpus_6-to-1', raw_d=dynamic_data['FLT'])
    ]
    visualize(data=data, x_lbl="VM (vcpus=6) Core Affinity", y_lbl="Mean Latency ("r'$\mu$'"s)",
              title="Real-Time Performance with HVM Shrink", out_plot_path="results/rt-vs-hvm-shrink.svg", type='eb')


def analyse(isolated_data, dynamic_data):
    anlz_isolated(isolated_data)
    anlz_dynamic(dynamic_data)
