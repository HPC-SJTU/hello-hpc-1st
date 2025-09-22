import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <your_answer>")
        sys.exit(1)
    with open("submit.zip","wb") as f:
        f.write(sys.argv[1].encode("utf-8"))
    print("generate submit.zip success")