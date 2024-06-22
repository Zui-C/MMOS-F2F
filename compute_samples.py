import json
import glob


for setting in [
    # 'llemma7b_minif2f-test/try',
    'llemma7b_minif2f-test/sample',
    # 'llemma34b_minif2f-test/try',
    'llemma34b_minif2f-test/sample',
    # 'deepseek-math-7b-base_minif2f-test/try',
    'deepseek-math-7b-base_minif2f-test/sample',
    'prover_mix3_k9_ep1_minif2f-test/llemma7',
    'prover_mix3_k9_ep1_minif2f-test/llemma34',
    'prover_mix3_k9_ep1_minif2f-test/deepseek',
    # 'prover_mix3_k9_ep1_minif2f-valid/llemma7',
    # 'prover_mix3_k9_ep1_minif2f-valid/llemma34',
    # 'prover_mix3_k9_ep1_minif2f-valid/deepseek',
    # './'
]:
    fs = []
    n = 0
    ns = 0
    total_iteration = 0
    nf = 0
    nf_search = 0
    nf_time = 0
    proof_finished_count_total = 0
    tactic_state_count_total = 0
    print('*'*50, setting, '*'*50)
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
                # if iteration > 50:
                #     print(name, iteration)
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
    print('proof_sample_rate', proof_finished_count_total, proof_finished_count_total/(n), proof_finished_count_total/(n*100*32))
    print('tactic_sample_rate', tactic_state_count_total, tactic_state_count_total/(n*100*32))

