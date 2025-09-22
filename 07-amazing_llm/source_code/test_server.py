from openai import OpenAI
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-port', type=int, default= 18000)

args = parser.parse_args()

work_dir = os.path.dirname(os.path.abspath(__file__))
client = OpenAI(api_key="111", base_url= f'http://localhost:{args.port}/v1')

def stream_completion(prompt, model_name):
    try:
        stream = client.completions.create(
            model=model_name,
            prompt= prompt,
            stream=True,
            temperature=0.8,
            seed= 42,
            max_tokens= 200 ,
        )
        
        answer_chars = []
        for chunk in stream:
            if chunk.choices[0].text is not None:
                print(chunk.choices[0].text, end="", flush=True)
                answer_chars.append(chunk.choices[0].text)
    
    except Exception as e:
        print(f"发生错误: {e}")
    return ''.join(answer_chars)

if __name__ == "__main__":
    user_input = "The meaning of life is"
    llm_path = "/lustre/share/xflops/amazing_llm/qwen3-8b-m3/"
    print("AI回复: ", end="")
    answer_chars = stream_completion(user_input, llm_path)
    with open(os.path.join(work_dir, "ans.txt") ,"w") as f:
        f.write(answer_chars)
    print("\nanswer saved in ans.txt")