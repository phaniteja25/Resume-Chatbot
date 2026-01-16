# Resume AI Chatbot

### About the project:
<p>The main aim of Resume Chatbot is to reduce the time taken by a recruiter to go through the myresume and instead directly talk to it and ask various questions about the candidate.
The AI tries to answer the question by taking in my resume in context and answer the question accordingly. If the question is out of contenxt, then the AI responds accordingly in a professional manner</p>

### Demo of the Project
https://github.com/user-attachments/assets/5f47776d-a1ca-4590-a65d-f29c1641dd4c

### Tech Stack used 
<ul>
  <li>Frontend - Streamlit</li>
  <li>Backend - Python</li>
  <li>LLM Model used - Gemini 2.5 Flash Lite</li>
  <li>Database - ChromaDB</li>
</ul>

### Steps to run the program 
<ol>
  <li>Clone the project</li>
  <li>Go to Google AI studio and generate an API key for the model named "gemini-2.5-flash-lite" </li>
  <li>Create .env file and put the generated API key as value to the key named "GEMINI_API_KEY" </li>
  <li>Now run the command "pip install -r requirement.txt" to install all the required libraries to run the project locally</li>
  <li>After successfull installation, run the command "streamlit run app.py". This will run the app locally and you can test it</li>
</ol>

<br/>

<a href = "https://teja-resume-chatbot.streamlit.app/">Demo Link</a>
