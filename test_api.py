print("LEMME COOK!")
import google.generativeai as genai

genai.configure(api_key="AIzaSyC1g7I9IiRbLFf4Agzj2FyFaM6urqaj6co")

model = genai.GenerativeModel("gemini-1.5-flash", system_instruction="You are sarcastic, old and angry chinese grandma")

response = model.generate_content("hi")

print(response.text)
