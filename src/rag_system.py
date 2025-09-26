import os
import chromadb  # vector db
from openai import OpenAI
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer  # for embeddings
import re
from typing import List, Dict
from dotenv import load_dotenv
import streamlit as st
from google import genai

# loading environment var
load_dotenv()


class ResumeRAG:
    def __init__(self):  # constructor
        print("Initializing the RAG system")

        # self.openai_key = os.getenv("OPEN_AI_API_KEY")
        # self.openai_client = OpenAI(api_key=self.openai_key)
        
        self.client = genai.Client()
        

        # Initializing the embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        #initliazing paths 
        current_file_dir = os.path.dirname(os.path.abspath(__file__))  
        project_root = os.path.dirname(current_file_dir)

        
        # chroma db setting up
        chroma_dir = os.path.join(project_root,"chroma_db")
        self.chroma_client = chromadb.PersistentClient(
            chroma_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection_name = "resume_collection"

        # creating collection
        try:
            self.collection = self.chroma_client.get_collection(
                self.collection_name
            )
            print("Connected to existing Resume Collection")
            print("Info :",self.collection.get())
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Resume content chunks"}
            )
            
            print("Created new Resume Collection")

            self.resume_path = os.path.join(project_root,"data","resume.txt")
            self.adding_resume_to_db(self.resume_path)
            
            
            print("Added resume to chromadb")

    def split_resume_into_chunks(self, file_path: str) -> List[Dict]:
        # reading the resume
        with open(file_path, "r", encoding="UTF-8") as resume:
            resume_content = resume.read()

        # splitting the resume to list of sections
        resume_sections = re.split(r'\n([A-Z\s&]+)\n', resume_content)

        chunks = []
        curr_section = ""

        for i, section in enumerate(resume_sections):
            if section.strip() and section.isupper():
                curr_section = section.strip()
                print("Current Section:", curr_section)

            elif section.strip():
                paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
                for para in paragraphs:
                    chunks.append(
                        {
                            "content": para,
                            "section": curr_section,
                            "id": f"{curr_section}_{len(chunks)}"
                        }
                    )

        print("Created Chunks of resume")
        return chunks

    def adding_resume_to_db(self, resume_path: str):
        chunks = self.split_resume_into_chunks(resume_path)

        # raise exception if chunks empty
        if not chunks:
            raise Exception("No content found in resume")

        print("Converting chunks to vectors")
        section_content = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_model.encode(section_content).tolist()

        # preparing data for chromaDB
        ids = [f"chunk_{i}" for i in range(len(chunks))]

        metaData = [
            {"section": chunk["section"]}
            for chunk in chunks
        ]

        # clear existing data if exists
        try:
            existing_data = self.collection.get()
            if existing_data["ids"]:
                self.collection.delete(ids=existing_data["ids"])
        except:
            pass

        # adding data in chunks to db in batches
        batch_size = 10
        for i in range(0, len(section_content), batch_size):
            batch_section_content = section_content[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            batch_metaData = metaData[i:i + batch_size]

            self.collection.add(
                embeddings=batch_embeddings,
                metadatas=batch_metaData,
                documents=batch_section_content,
                ids=batch_ids
            )

        print(f"Added {len(chunks)} chunks to the Chroma DB")
        return len(chunks)

    # returns a list of relevant text or chunks for the given query
    def retrieve_relevant_info(self, query: str, n_results: int = 3) -> List[str]:
        print(f"Searching for: '{query}'")

        query_embedding = self.embedding_model.encode([query]).tolist()
        print("Query converted to vector embedding")

        # query the vector db for similar embeddings to that of query
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(n_results, self.collection.count())
        )

        relevant_chunks = results["documents"][0] if results["documents"] else []

        for i, chunk in enumerate(relevant_chunks[:2]):  # Show first 2
            print(f"Chunk {i+1} preview: {chunk[:100]}...")

        return relevant_chunks

    def generate_response(self, query: str, context: List[str]) -> str:
        if not context:
            return (
                "I don't have information about that in my resume. "
                "Could you ask about my experience, skills, or projects?"
            )

        combined_context_text = "\n\n".join(context)
        print(f"Context length: {len(combined_context_text)} characters")

        user_prompt = f"""You are a professional AI assistant representing Saimanikanta Phani Teja U based on his resume. 
You should answer questions about his background, experience, and skills in a conversational, 
manner as if you are speaking on his behalf to a recruiter in a third person manner.

Key guidelines:
- Be professional but personable
- Use "He or his" statements (e.g., "He has experience with...")
- Only discuss information provided in the resume context
- If asked about something not in the resume, politely redirect to topics you can discuss
- Keep responses concise but informative (2-4 sentences typically)
- Highlight specific achievements and technologies when relevant

 Based on this resume information:

{combined_context_text}

Question: {query}

Please provide a conversational, third-person response as Teja."""

        try:
            # Check API key availability
           
            if not self.client:
                return "Error creating gemini client"

            print("Generating response with OpenAI...")

            # Calling OpenAI API
            # response = self.openai_client.responses.create(
            #     model="gpt-5-nano",
            #     input=[
            #         {"role": "system", "content": system_prompt},
            #         {"role": "user", "content": user_prompt}
            #     ],
            #     max_output_tokens=300
            # )

            #calling gemini 
            response = self.client.models.generate_content(
                model = "gemini-2.5-flash-lite",
                contents=user_prompt
            )
            generated_text = response.text.strip()
            print(f"Generated response: {len(generated_text)} characters")

            return generated_text

        except AttributeError as e:
            # Handle issues with API client or response
            print(f"Error: {e}")
            return "There was an error generating the response."
        
        
    
    def chat(self, query: str) -> str:
        """Main chat function - the one users will call."""
        print(f"\n--- Processing query: '{query}' ---")
        
        # Step 1: Check if database has data
        try:
            db_count = self.chroma_client.get_collection(self.collection_name).count()
            db_info = self.collection.get()
            print(f"This is the Chroma DB info : {db_info}")
            if db_count == 0:
                return "My resume data hasn't been loaded yet. Please initialize the system first."
            print(f"Database has {db_count} chunks available")
        except Exception as e:
            return f"Error accessing resume database: {str(e)}"
        
        # Step 2: Find relevant resume information
        relevant_info = self.retrieve_relevant_info(query, n_results=3)
        
        # Step 3: Generate natural response
        response = self.generate_response(query, relevant_info)
        
        print("--- Response generated ---\n")
        return response



def main():
    #initializing the Rag system
    ResumeGenerator = ResumeRAG()
        
    response = ResumeGenerator.chat("Explain about his experience at Paycom")
        
    print(response)
        
    
if __name__ == "__main__":
    
    main()
        
        
        
