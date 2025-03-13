import re

def parse_ranges(input_str):
    elements = input_str.split(',')
    result = []
    prev_value = None
    
    for elem in elements:
        if re.match(r'^[A-Za-z]', elem):
            prev_value = int(elem.split('-')[1])
        else:
            start = prev_value #+ 1
            size = int(elem.split('-')[1]) + 1  # Increase size by 1
            result.append((start, size))
            prev_value = None  # Reset prev_value after using it
    
    return result

def modify_string(data_str, ranges):
    half_size = len(data_str) // 2
    data_list = list(data_str)  # Convert to list for mutability
    
    for index, size in ranges:
        if index < half_size:
            start_replace = index + half_size
            data_list[start_replace:start_replace + size] = data_list[index:index + size]
        else:
            start_replace = index - half_size
            data_list[start_replace:start_replace + size] = data_list[index:index + size]
    
    modified_str = ''.join(data_list)
    return modified_str[:half_size].strip(), modified_str[half_size:].strip()

# Example Usage
contigs = "A1-142,11-11,A154-216,9-9,A226-355,7-7,A363-392,8-8,A401-610"
sequence = "MLTDIDGIRVGHATDARAMTGCTIAVFDEPVVPGVDVRGANAATIYTDLLYPDSVMPSVTGIMLTGGSAFGLEAALGAVRYFEEQGRGYDVGVAKIPLVPAAVIYDLSVGDANVRPDLAMGRRACEAAKPGPFERGRVGGGTZZZZZZZZZZZQSSPGGLGTATVSLYGGIKVSAMIVVNSFGDLRDTAGRIVAGAKYEGGEFADTYARMKLGDKNZZZZZZZZZNTTIGIVSTNCRLTKVEASRMATLAHNGLARAICPIHTNVDGDTIFATGLQKSDLTAPVDLLGTAAAEAAMLACLDAVMQMLTDIDGIRVGHATDARAMTGCTIAVFDEPVVPGVDVRGANAATIYTDLLZZZZZZZSVTGIMLTGGSAFGLEAALGAVRYFEEQGRZZZZZZZZIPLVPAAVIYDLSVGDANVRPDLAMGRRACEAAKPGPFERGRVGGGTGATVGKLYGVRQSSPGGLGTATVSLYGGIKVSAMIVVNSFGDLRDTAGRIVAGAKYEGGEFADTYARMKLGDKNQSALARMGMNTTIGIVSTNCRLTKVEASRMATLAHNGLARAICPIHTNVDGDTIFATGLQKSDLTAPVDLLGTAAAEAAMLACLDAVMQ" #input string

ranges = parse_ranges(contigs)
a_string, d_string = modify_string(sequence, ranges)

print(">chain_a\n" + a_string)
print(">chain_d\n" + d_string)
