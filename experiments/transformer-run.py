#!/usr/bin/env python

from transformers import TFAutoModelForCausalLM, AutoTokenizer

model = TFAutoModelForCausalLM.from_pretrained("gpt4chan_model/config.json").to("cpu")
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B", local_files_only=True, from_pt=True, device_map="cpu")

prompt = (
    "In a shocking finding, scientists discovered a herd of unicorns living in a remote, "
    "previously unexplored valley, in the Andes Mountains. Even more surprising to the "
    "researchers was the fact that the unicorns spoke perfect English."
)

input_ids = tokenizer(prompt, return_tensors="pt").to("cpu").input_ids

gen_tokens = model.generate(
    input_ids,
    do_sample=True,
    temperature=0.8,
    top_p=0.9,
    max_length=100,
)
gen_text = tokenizer.batch_decode(gen_tokens)[0]
