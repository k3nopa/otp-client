import glob

dir = "a_1000_n_128_h_8"
parsed = {}

class Data:
    def __init__(self, key, layer) -> None:
        self.key = key
        self.layer = layer

    def trans(self):
        return {self.layer : self.key}

def parse_sample(filename, k):
    total = 0
    layer2key = {}

    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            if 'Session' in line:
                total += 1
                parts = line.split(' ')

                path = parts[5]
                key = parts[7]
                layer = parts[10]
                
                if int(layer) < k: continue

                data = Data(key, layer)
                if layer2key.get(path) == None:
                    layer2key[path] = [data]
                else:
                    curr = layer2key[path]
                    curr.append(data)
                    layer2key[path] = curr

    file_name = filename.split('.')[0]
    parsed[file_name] = { 'total session' : total }

    parsed[file_name]['path_keylen'] = {}
    for path in layer2key:
        parsed[file_name]['path_keylen'][path] = [x.layer for x in layer2key[path]]

    # Find duplicate keys in layer2key.
    parsed[file_name]['dups'] = {}
    for path in layer2key:
        data = layer2key[path]
        if len(data) == 1:
            continue
        else:
            no_dups = set(x.key for x in data)
            dups_pair = []
            if len(no_dups) != len(data):
                count = 0
                for x in no_dups:
                    for y in data:
                        if x == y.key: 
                            count += 1
                            if count > 2: 
                                dups_pair.append([x, y.key])

            if len(dups_pair) > 0:
                parsed[file_name]['dups'][path] = dups_pair

def report_result(data):
    total_samples = len(data)

    print("Samples\t\tTotal Sessions")
    total_sum = 0
    for i in range(1, total_samples+1):
        file = f"{dir}/sample{i}"
        sample = file.split('/')[-1]

        space = ''
        if i <= 9:
            space = '\t\t'
        else:
            space = '\t'

        print(f"{sample}{space}{data[file]['total session']}")
        total_sum += data[file]['total session']
    print(f"Avg Total Session: {total_sum/total_samples:.3f}")

    print("\nSamples\t\tAvg Key Len")
    sample_avg = []
    for i in range(1, total_samples+1):
        total_sum = 0
        file = f"{dir}/sample{i}"
        sample = file.split('/')[-1]
        
        for path in data[file]['path_keylen']:
            if len(data[file]['path_keylen'][path]) > 1:
                for x in data[file]['path_keylen'][path]:
                    total_sum += int(x)
            else:
                total_sum += int(data[file]['path_keylen'][path][0])

        avg = total_sum/int(data[file]['total session']) 
        sample_avg.append(avg)

        space = ''
        if i <= 9:
            space = '\t\t'
        else:
            space = '\t'

        print(f"{sample}{space}{avg:.3f}")

    print(f"Avg Key Len: {sum(sample_avg)/total_samples:.3f}")

    print("\nSamples\t\tAvg Duplicates")
    total_sum = 0
    for i in range(1, total_samples+1):
        file = f"{dir}/sample{i}"
        sample = file.split('/')[-1]

        dups_list = data[file]['dups']
        dup_pair = {}   # Store path to array of duplicate keys.
        total = 0

        space = ''
        if i <= 9:
            space = '\t\t'
        else:
            space = '\t'

        if len(dups_list) == 0:
            print(f"{sample}{space}0")
            continue
        else:
            for path in dups_list:
                dups_len = len(dups_list[path])
                total += dups_len
                dup_pair[path] = dups_len

            if len(dup_pair) != 0:
                print(f"{sample}{space}{total/len(dup_pair)}")
                total_sum += total/len(dup_pair)
            else: 
                print(f"{sample}{space}{total/1}")
                total_sum += total/1

    print(f"\nAvg Duplicate: {total_sum/total_samples}")

files = glob.glob(f"{dir}/*.txt")
target_k = 80

for file in files:
    parse_sample(filename=file, k = target_k)

# from pprint import pprint
# pprint(parsed[f'{dir}/sample2'])

report_result(parsed)
