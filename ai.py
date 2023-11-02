import openai
from data import AI_TOKEN


openai.api_key = AI_TOKEN
message = 'Реши физическую задачу: Давление воды в цилиндре нагнетательного насоса 1200 кПа. Чему равна работа при' \
          ' перемещении поршня площадью 400 см2 на расстояние 50 см.'
response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=message,
  temperature=0.5,
  max_tokens=256
)

print(response['choices'][0]['text'])