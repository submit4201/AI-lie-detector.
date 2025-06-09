import dspy
from backend.config import GEMINI_API_KEY

# 1. Define a simple DSPy signature
class BasicQA(dspy.Signature):
    """A basic question-answering signature."""
    question = dspy.InputField(desc="The question to answer.")
    answer = dspy.OutputField(desc="The answer to the question.")

# 2. Define a simple DSPy module
class BasicModule(dspy.Module):
    """A basic DSPy module."""
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(BasicQA)

    def forward(self, question):
        return self.predictor(question=question)

if __name__ == "__main__":
    # 3. Initialize dspy.LM with the GEMINI_API_KEY and model
    model_name = "models/gemini-1.5-flash-latest" # Ensure this model name is accurate for your access
    # The documentation uses 'gemini/model-name' format
    dspy_model_string = f"gemini/{model_name.split('/')[-1]}"
    try:
        gemini_lm = dspy.LM(dspy_model_string, api_key=GEMINI_API_KEY)

        # 4. Configure dspy.settings with the initialized Gemini language model
        dspy.settings.configure(lm=gemini_lm)

        # 5. Instantiate BasicModule
        basic_module = BasicModule()

        # 6. Define a sample question
        sample_question = "What is the capital of France?"

        # 7. Call the module's forward method with the question
        response = basic_module.forward(question=sample_question)

        # 8. Print the question and the returned answer
        print(f"Question: {sample_question}")
        print(f"Answer: {response.answer}")

    except Exception as e:
        print(f"An error occurred during the DSPy basic integration test: {e}")
        print("Please ensure your GEMINI_API_KEY is correctly configured in backend/config.py and that the model is available.")
        print(f"Attempted to use model string: {dspy_model_string}")
