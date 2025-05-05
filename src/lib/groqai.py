class GroqAI:
    def __init__(
        self,
        system_prompt=None,
        model="llama3-70b-8192",
        max_tokens=1500,
        temperature=0.1,
        api_key=None,
    ):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.set_system(system_prompt)

    def set_system(self, prompt):
        self.prompt = (
            prompt
            or "You are a helpful assistant. You reply with short, accurate answers."
        )
        self.system_prompt = {"role": "system", "content": self.prompt}
        self.chat_history = [self.system_prompt]

    def says(self, prompt):
        self.chat_history.append({"role": "user", "content": prompt})
        # sys.stderr.write(f"history: {self.chat_history}\n")
        response = self.groq_client.chat.completions.create(
            model=self.model,
            messages=self.chat_history,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        self.chat_history.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )
        return response.choices[0].message.content
