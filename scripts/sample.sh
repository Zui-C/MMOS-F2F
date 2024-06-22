set -ex
cd /PATH/llemma_formal2formal
export CONTAINER="native"
source $HOME/.elan/env
lake


# ---
MAX_ITERS=100
NUM_SAMPLES=32
TEMPERATURES="0.0"
TIMEOUT=600
DATASET="minif2f-valid"
DATA="data/minif2f.jsonl"
NAME="llemma7b"
MODEL="/PATH"
JOB_NAME="sample"
OUTPUT_DIR="output/${NAME}_${DATASET}"

BATCH_JOB_ID=1
START_GLOBAL=0
END_GLOBAL=1
BATCH_JOB_NUM=1
GPUS_PER_GROUP=1  # 每个任务需要几张显卡
GPU_GROUPS_PER_BATCH=1 # 每个批次有4组，共 8 个显卡
# ---
TOTAL_TEST_NUM=$((END_GLOBAL - START_GLOBAL))
SHARD=$((BATCH_JOB_ID))


# 计算每个批次的大小
BATCH_SIZE=$((TOTAL_TEST_NUM / BATCH_JOB_NUM))

# 对每个批次进一步切分，每组显卡一个小批次
SUB_BATCH_SIZE=$((BATCH_SIZE / GPU_GROUPS_PER_BATCH))

# 计算当前批次的开始
START=$(( START_GLOBAL + (BATCH_JOB_ID - 1) * BATCH_SIZE ))
if [ "${BATCH_JOB_ID}" -eq "${BATCH_JOB_NUM}" ]; then
    END=$END_GLOBAL
else
    END=$(( START + BATCH_SIZE ))
fi

# 准备多组显卡
declare -a GPU_GROUPS
for (( GROUP_ID=0; GROUP_ID<GPU_GROUPS_PER_BATCH; GROUP_ID++ ))
do
    GPU_GROUP=""
    for (( GPU_ID=0; GPU_ID<GPUS_PER_GROUP; GPU_ID++ ))
    do
        GPU_INDEX=$(( GROUP_ID * GPUS_PER_GROUP + GPU_ID ))
        if [ -n "$GPU_GROUP" ]; then
            GPU_GROUP="${GPU_GROUP},"
        fi
        GPU_GROUP="${GPU_GROUP}${GPU_INDEX}"
    done
    GPU_GROUPS[GROUP_ID]=$GPU_GROUP
done


# 循环分配每组显卡的任务
for (( GROUP_ID=0; GROUP_ID<GPU_GROUPS_PER_BATCH; GROUP_ID++ ))
do
    GPU_START=$(( START + GROUP_ID * SUB_BATCH_SIZE ))
    GPU_END=$(( GPU_START + SUB_BATCH_SIZE ))

    # 确保最后一组的子批次不超过大批次的END
    if [ "$GROUP_ID" -eq $((GPU_GROUPS_PER_BATCH - 1)) ]; then
        GPU_END=$END
    fi

    CUDA_VISIBLE_DEVICES=${GPU_GROUPS[GROUP_ID]}

    echo "Running batch job id ${BATCH_JOB_ID}, GPU group ${GROUP_ID}, START=${GPU_START}, END=${GPU_END}, GPUs=${CUDA_VISIBLE_DEVICES}"

    CUDA_VISIBLE_DEVICES=${GPU_GROUPS[GROUP_ID]} TOKENIZERS_PARALLELISM=false \
    python few_shot.py \
        --dataset-name ${DATASET} \
        --temperatures ${TEMPERATURES} \
        --timeout ${TIMEOUT} \
        --shard ${SHARD} \
        --start ${GPU_START} \
        --end ${GPU_END} \
        --model-name ${MODEL} \
        --max-iters ${MAX_ITERS} \
        --dataset-path ${DATA} \
        --num-samples ${NUM_SAMPLES} \
        --early-stop \
        --output-dir ${OUTPUT_DIR} \
        --job ${JOB_NAME} \
        2>&1 | tee log/${NAME}_shard${SHARD}.out
done
wait # 等待所有后台任务完成


