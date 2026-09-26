from llm import call_llm

if __name__ == "__main__":
    result = call_llm([
        {"role": "user", "content": "Reply with exactly: LLM_OK"}
    ])
    print(result)
