import streamlit as st
from streamlit_chat import message

from database import get_redis_connection
from chatbot import RetrievalAssistant, Message
import shutil
import os
import datetime
import hashlib

# Initialise database

## Initialise Redis connection
redis_client = get_redis_connection()

# Set instruction

# System prompt requiring Question and Year to be extracted from the user
system_prompt = '''
You are a helpful HKSTP based knowledge base assistant. You need to capture the Question of each customer.
The Question is their query on HKSTP.
Think about this step by step:
- The user will ask a Question about HKSTP
- Once you have the Question, and find the related info list the anser and the source where you find the answer, your answer is based on the training data, 
- if you couldn't find the info, just say : sorry, I don't knom, please contact HKSTP BD Team/26296991 for detaied info

Example:

User: I'd like to know the admission criteria for HKSTP Incubation program

Assistant: Certainly, Searching for answers.
'''

### CHATBOT APP

st.set_page_config(
    page_title="Streamlit Chat - Demo",
    page_icon=":robot:"
)

st.markdown("""
    <a href="/en/">
        <img src="https://www.hkstp.org/assets/images/HKSTP_logo_ENG_OP-01.svg" class="img-logo-white">
      
""", unsafe_allow_html=True)

st.title('HKSTP Chatbot')
st.markdown("<h3 style='color: blue; font-size: 20px;'>Help us help you learn about HKSTP_Your Success Is Our Success</h3>", unsafe_allow_html=True)

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def query(question):
    response = st.session_state['chat'].ask_assistant(question)
    return response

prompt = st.text_input(f"What do you want to know about HKSTP: ", key="input")

if prompt: # 如果有输入

    # Initialization
    if 'chat' not in st.session_state:
        st.session_state['chat'] = RetrievalAssistant()
        messages = []
        system_message = Message('system',system_prompt)
        messages.append(system_message.message())
    else:
        messages = []

    user_message = Message('user',prompt)
    messages.append(user_message.message())

    response = query(messages)

    # Debugging step to print the whole response
    #st.write(response)

    st.session_state.past.append(prompt)
    st.session_state.generated.append(response['content'])

if st.session_state['generated']:
    st.write('## Chat History')
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

    response = query(messages)

    # Debugging step to print the whole response
    #st.write(response)

    st.session_state.past.append(prompt)
    st.session_state.generated.append(response['content'])

        
        
        
        
        
        
# Using object notation
add_selectbox = st.sidebar.selectbox(
    "Choose a LLM Model",
    ("gpt-3.5-turbo", "text-davinci-003", "gpt-4")
)

# 在侧边栏创建一个文本框
api_key = st.sidebar.text_input("Input API Key")

# 显示输入的 API Key
#st.sidebar.write("API_KEY：", api_key)


# 在侧边栏创建一个数字输入框
number = st.sidebar.number_input("Temepature", min_value=0.1, max_value=1.0, value=0.5)

# 提示temeperature
my_string = "Higher temperature value: more creative responses, <br>Lower temperature value: More accurate and coherent responses"

# 使用 st.markdown 方法显示字符串，设置字体大小和颜色
st.sidebar.markdown(f"<p style='font-size: 10px; color: black;'>{my_string}</p>", unsafe_allow_html=True)


# 创建侧边栏
sidebar = st.sidebar

# 添加文本框和下拉菜单选项
top_k = sidebar.text_input("Top_K:", value="10")
embedding_chunk = sidebar.selectbox("Embedding Chunk:", options=[32, 64, 128], index=0)

# 在主页面中显示选项值
#st.write("Top K:", top_k)
#st.write("Embedding Chunk:", embedding_chunk)
        
language = st.sidebar.selectbox(
    "Please select a language:",
    ["English", "Chinese", "Japanese", "Korean"]
)

    
#定义 CSS 样式表
css = """
body {
    background-image: url("https://upload.wikimedia.org/wikipedia/zh/thumb/9/97/Hong_Kong_Science_%26_Technology_Parks.svg/1200px-Hong_Kong_Science_%26_Technology_Parks.svg.png");
    background-repeat: no-repeat;
    background-size: cover;
}
"""
# 将样式表添加到应用程序中
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
 



import os

# 创建侧边栏
sidebar = st.sidebar

# 创建添加文本按钮
if sidebar.button("Input corpus"):
    # 在侧边栏中显示新页面
    with st.sidebar.expander("Input corpus"):
        # 获取用户输入
        user_input = st.text_input("please input the content", value="", key="user_input")

        # 获取主题subject
        subject = st.text_input("Subject")

        # 设置CSS样式c
        st.markdown("""
        <style>
        .stTextInput {
            height: 200px;
        }
        .add-text {
            margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

        # 在subject下方添加HTML标记，设置标记的style属性
        st.write(
            "<div style='margin-top: 5px'><hr style='margin-bottom: 5px'><div class='add-text'></div></div>",
            unsafe_allow_html=True
        )

        # 检查用户是否输入了文本
        if user_input:
            # 创建保存按钮
            if st.button("保存"):
                # 生成文件名和摘要
                now = datetime.datetime.now()
                if subject:
                    file_name = now.strftime("%Y%m%d%H%M%S") + "_" + subject.replace(" ", "_") + ".txt"
                else:
                    file_name = now.strftime("%Y%m%d%H%M%S") + "_" + hashlib.md5(user_input.encode()).hexdigest()[:8] + ".txt"
                file_summary = user_input[:50] + "..."

                # 生成完整文件路径
                file_path = os.path.join("/Users/zhangning/github/openai-cookbook/apps/chatbot-kickstarter/Traindata", file_name)

                # 将文本写入本地txt文件
                with open(file_path, "w") as f:
                    f.write(user_input)
                st.success("文本已成功保存到本地txt文件！")

                # 显示文件名和摘要
                st.write("文件名：", file_name)
                st.write("摘要：", file_summary)


# 在侧边栏创建一个多文件上传框和一个文本框
uploaded_files = st.sidebar.file_uploader("Upload", type=["csv", "txt","pdf","doc","excel"], accept_multiple_files=True)
folder_path = "/Users/zhangning/github/openai-cookbook/apps/chatbot-kickstarter/Traindata"

# 如果有文件上传，保存每个文件到指定的文件夹中
if uploaded_files is not None:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(folder_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.write(f"文件已保存到本地文件夹中：{file_path}")
        


    
# Divide the sidebar into two columns and place the "Train" and "View Corpus" buttons in separate columns
col1, col2 = st.sidebar.columns(2)
with col1:
    train_button = st.button("Train")

if train_button:
    st.write("Submitting training, please wait...")

with col2:
    view_corpus_button = st.button("View Corpus")

if view_corpus_button and uploaded_files is not None:
    for uploaded_file in uploaded_files:
        file_contents = uploaded_file.read()
        st.write("File Name:", uploaded_file.name)
        st.write("File Content:")
        st.write(file_contents)