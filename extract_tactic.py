import json
import glob
import os
import json


def construct_sample(tactic, state_before):
    """
    Tactic state:
    ---
    α : Type u_1
    r : α → α → Prop
    inst✝¹ : DecidableEq α
    inst✝ : IsIrrefl α r
    ⊢ CutExpand r ≤ InvImage (Finsupp.Lex (rᶜ ⊓ fun x x_1 => x ≠ x_1) fun x x_1 => x < x_1) ↑toFinsupp
    ---
    Next tactic:
    ---
    rintro s t ⟨u, a, hr, he⟩
    ---

    """

    full_prompt = f'Tactic state:\n---\n{state_before.strip()}\n---\nNext tactic:\n---\n'
    completion = f'{tactic.strip()}\n---'


    return full_prompt,completion




samples = []
dedup_samples = []
for setting in [
    # 'llemma7b_minif2f-test/try',
    # 'deepseek-math-7b-base_minif2f-test/try'
    'llemma34b_minif2f-valid/sample',
    'llemma7b_minif2f-valid/sample',
    'deepseek-math-7b-base_minif2f-valid/sample'
    # './'
]:
    print('*'*50, setting, '*'*50)
    n = 0
    ns = 0
    total_iteration = 0
    nf = 0
    nf_search = 0
    nf_time = 0
    proof_finished_count_total = 0
    tactic_state_count_total = 0
    fs = []
    for x in glob.glob('./output/%s/*.json' % setting):
        # print(x)
        fs.append(json.load(open(x)))
    print('file_count', len(fs))


    for f in fs:
        for result in f['results']:
            name = result['example']['full_name']

            # Extra helper theorem in the OpenAI code
            if 'sum_pairs' in name:
                continue

            n += 1
            if result['success']:
                ns += 1
                iteration = result['attempt_results'][0]['iteration']
                # print(iteration)
                total_iteration += iteration
                if iteration > 50:
                    print(name, iteration)
            else:
                failure_reason = result['attempt_results'][0]['failure_reason']
                nf += 1
                # print(failure_reason)
                if failure_reason == 'SearchEnded':
                    nf_search += 1
                elif failure_reason == 'DojoHardTimeoutError':
                    nf_time += 1
                
            
            # 统计采样率
            # print('*'*50)
            iters_info = result['iters_info']
            for iter in iters_info:
                type = iter['type']
                tactic_state_count = type.count('TacticState')
                proof_finished_count = type.count('ProofFinished')
                else_count = type.count('else')
                if tactic_state_count + proof_finished_count + else_count != 32:
                    assert tactic_state_count + proof_finished_count + else_count != 32
                proof_finished_count_total += proof_finished_count
                tactic_state_count_total += tactic_state_count

    print('setting', 'ns', 'n', 'ns/n',  'nf', 'nf_search', 'nf_time', sep='\t')
    print(setting, ns, n,  ns/n, nf, nf_search, nf_time, sep='\t')
    print('average_iteration', total_iteration/ns)
    print('proof_sample_rate', proof_finished_count_total, proof_finished_count_total/(n*100*32))
    print('tactic_sample_rate', tactic_state_count_total, tactic_state_count_total/(n*100*32))
    for f in fs:
        for result in f['results']:
            name = result['example']['full_name']
            iters_info = result['iters_info']
            for iter_info in iters_info:
                steps = iter_info['step']
                types = iter_info['type']
                tactic_state = iter_info['tactic_state']
                for i,step in enumerate(steps):
                    if types[i] == 'ProofFinished' or types[i] == 'TacticState':
                        full_prompt, completion = construct_sample(step,tactic_state)
                        sample = {
                            'example': result['example'],
                            'prompt': full_prompt,
                            'completion': completion
                        }
                        samples.append(sample)
                    
                        
print('sample_count', len(samples))


train_data_name = 'mix3'
output_dir = f'./tactics/{train_data_name}'
os.makedirs(output_dir, exist_ok=True)
sample_path = f'{output_dir}/samples.jsonl'
dedup_sample_path = f'{output_dir}/dedup_samples.jsonl'
train_data_path = f'{output_dir}/train.jsonl'
k = 3
train_rs_data_path = f'{output_dir}/train_rs{k}.jsonl'


with open(sample_path, 'w') as f:
    for sample in samples:
        f.write(json.dumps(sample)+'\n')


        
# 去重操作
filtered_data = []
seen_prompts_completions = set()       

for item in samples:
    prompt = item['prompt']
    completion = item['completion']
    if (prompt, completion) not in seen_prompts_completions:
        seen_prompts_completions.add((prompt, completion))
        filtered_data.append(item)
print('dedup_sample_count', len(filtered_data))
with open(dedup_sample_path, 'w') as f:
    for item in filtered_data:
        f.write(json.dumps(item)+'\n')
        
# 对 filtered_data 进行shuffle作为训练数据，只保留prompt和completion并在开始增加idx
import random
filtered_data_shuffle = filtered_data.copy()
# 随机打乱数据
random.seed(0)
random.shuffle(filtered_data_shuffle)

train_data = []
for idx, item in enumerate(filtered_data_shuffle):
    train_data.append({
        'idx': idx,
        'prompt': item['prompt'],
        'completion': item['completion']
    })

with open(train_data_path, 'w') as f:
    for item in train_data:
        f.write(json.dumps(item)+'\n')
        
        
        
        
# random select 
from collections import Counter, defaultdict
source_counts = defaultdict(list)

# Read the file and count the source values
for item in filtered_data:
    # print(item)
    # source = item['example']['full_name']
    source = item['prompt']
    source_counts[source] += [item]
    # print(source_counts)
    # exit()
# 随机抽取k个
random_select_data = []
for source, items in source_counts.items():
    if len(items) > k:
        random_select_data.extend(random.sample(items, k))
    else:
        random_select_data.extend(items)
    

train_rs_data = []
for idx, item in enumerate(random_select_data):
    train_rs_data.append({
        'idx': idx,
        'prompt': item['prompt'],
        'completion': item['completion']
    })
with open(train_rs_data_path, 'w') as f:
    for idx, item in enumerate(train_rs_data):
        f.write(json.dumps(item)+'\n')
print(f'random select {k}', len(train_rs_data))
