import streamlit as st
from pathlib import Path
import base64

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

def set_css():
    st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-family: Arial, sans-serif;
        color: #4a4a4a;  /* You can change the color */
    }
    </style>
    """, unsafe_allow_html=True)

def display_filtered_message(message):
    # Use Markdown with the custom style class
    st.markdown(f'<p class="big-font">{message}</p>', unsafe_allow_html=True)



# Main function for the Streamlit app
def main():
    st.set_page_config(page_title="Hate Speech Filter", layout="wide", page_icon="🔍")

    st.title("Hate Speech Filter 🔎")

    def get_base64_encoded_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    def full_page_background_image_base64():
        image_path = Path(__file__).parent/'image/wallpaper2.jpg'
        #image_path = "wallpaper2.jpg"  # Update this path
        encoded_image = get_base64_encoded_image(image_path)
        css = f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{encoded_image}");
                background-size: cover;
                background-repeat: no-repeat;
                background-position: center;
            }}
            </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    full_page_background_image_base64()

    # Load the filter
    gfw = load_filter()

    # Text input
    user_input = st.text_area("Enter a message to filter:", height=150)
    if st.button("Filter Message"):
        if user_input:
            
            filtered_message = gfw.filter(user_input)
           
            #st.write("Filtered Message:", filtered_message)
            display_filtered_message(filtered_message)
           
        else:
            st.warning("Please enter a message to filter.")

if __name__ == "__main__":
    main()
