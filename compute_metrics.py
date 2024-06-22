import json
import glob


for setting in [
    'llemma7b_minif2f-valid/sample',
    'llemma34b_minif2f-valid/sample',
    'deepseek-math-7b-base_minif2f-valid/sample',
    
    'llemma7b_minif2f-test/sample',
    'llemma34b_minif2f-test/sample',
    'deepseek-math-7b-base_minif2f-test/sample',
    'prover_mix3_k9_ep1_minif2f-test/llemma7',
    'prover_mix3_k9_ep1_minif2f-test/llemma34',
    'prover_mix3_k9_ep1_minif2f-test/deepseek',
    'prover_mix3_k9_ep1_minif2f-valid/llemma7',
    'prover_mix3_k9_ep1_minif2f-valid/llemma34',
    'prover_mix3_k9_ep1_minif2f-valid/deepseek',
    'prover_tactics_mix3_k3_ep1_minif2f-test/llemma7b',
    'prover_tactics_mix3_k9_ep1_minif2f-test/llemma7b',
    'prover_mix3_r2_k9_ep1_minif2f-test/llemma7',


]:
    fs = []

    for x in glob.glob('./output/%s/*.json' % setting):
        # print(x)
        fs.append(json.load(open(x)))
    # print(len(fs))
    n = 0
    ns = 0
    total_iteration = 0
    iteration_less_3 = 0
    nf = 0
    nf_search = 0
    nf_time = 0
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
                    # print(name, iteration)
                    pass
                elif iteration < 3:
                    iteration_less_3 += 1
            else:
                failure_reason = result['attempt_results'][0]['failure_reason']
                nf += 1
                # print(failure_reason)
                if failure_reason == 'SearchEnded':
                    nf_search += 1
                elif failure_reason == 'DojoHardTimeoutError':
                    nf_time += 1
                
                
    # print('setting', 'ns', 'n', 'ns/n',  'nf', 'nf_search', 'nf_time','average_iteration', sep='\t')
    print(setting, ns, n,  ns/n, nf, nf_search, nf_time, total_iteration/ns, sep='\t')
    # print('average_iteration', total_iteration/ns)
    
