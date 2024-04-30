import streamlit as st


# DFA Algorithm
class DFAFilter():
    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword):
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, encoding='utf-8') as f:
            for keyword in f:
                self.add(str(keyword).strip())

    def filter(self, message, repl="*"):
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)

# Load the filter with caching
@st.cache_data
def load_filter():
    gfw = DFAFilter()
    #path = "sensitive_words.txt"  # Update the path to your keywords file
    path = Path(__file__).parent /'data/sensitive_words.txt'
    gfw.parse(path)
    return gfw

# Main function for the Streamlit app
def main():
    st.set_page_config(page_title="Hate Speech Filter", layout="wide", page_icon="🔍")

    st.title("Hate Speech Filter 🔎")

    # Load the filter
    gfw = load_filter()

    # Text input
    user_input = st.text_area("Enter a message to filter:", height=150)
    if st.button("Filter Message"):
        if user_input:
            
            filtered_message = gfw.filter(user_input)
           
            st.write("Filtered Message:", filtered_message)
           
        else:
            st.warning("Please enter a message to filter.")

if __name__ == "__main__":
    main()
