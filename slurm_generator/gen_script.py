import os

def gen_script(disc):
    layers = disc.replace(' ', '').split(',')
    n_layers = len(layers)
    base_id = f'{n_layers}L_' + '_'.join(layers)
    id = base_id
    exists = True
    num = 1

    base_path = os.path.join('..')
    while exists:
        id = base_id + (f"_R{num}" if num > 1 else '')
        output_path = os.path.join(base_path, 'outputs', f'run{id}')
        num += 1
        exists = os.path.exists(output_path)

    os.makedirs(output_path)
    print(id)

    binning_path = os.path.join(base_path, 'datas', 'data', f'binning_{id}.xml')
    with open(binning_path, 'w') as output:
        with open(f'binning_gen.xml', 'r') as input:
            for line in list(input):
                output.write(line.replace("####", ','.join(layers)))

    file_name = f'run_container_{id}.x'
    run_container_path = os.path.join(base_path, 'runs', file_name)
    with open(run_container_path, 'w') as output:
        with open(f'run_container_gen.x', 'r') as input:
            for line in list(input):
                output.write(line.replace('$$$', '|'.join(layers)).replace("####", id))
    print(f'Per eseguire:\n\tsbatch {run_container_path}')


if __name__ == "__main__":
    disc = input("Inserire configurazione discriminatore [L1,L2,L3,...,LN]: ")
    gen_script(disc)
