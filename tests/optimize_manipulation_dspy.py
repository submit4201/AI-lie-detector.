import dspy
import json
from backend.dspy_modules import DSPyManipulationAnalyzer
from backend.models import ManipulationAssessment # Not directly used by metric, but good for context
from backend.services.gemini_service import GeminiService # To trigger LM configuration
from dspy.teleprompt import BootstrapFewShot

# 1. DSPy LM Configuration
# This will initialize GeminiService and configure dspy.settings.lm if not already done.
print("Attempting to configure DSPy LM...")
gs_instance = GeminiService()
if not dspy.settings.lm:
    raise RuntimeError("DSPy LM not configured! Ensure GeminiService is setting it up.")
else:
    print(f"DSPy LM configured successfully with: {dspy.settings.lm.__class__.__name__}")


# 2. Define Sample Training Data (trainset)
trainset = [
    dspy.Example(
        transcript="You always make me feel like I'm not good enough. If you really cared, you wouldn't question me.",
        session_context="{}",
        is_manipulative=True,
        manipulation_score=0.8,
        manipulation_techniques=["Guilt-tripping", "Gaslighting"],
        manipulation_explanation="The speaker uses guilt ('if you really cared') and tries to make the listener doubt their perception ('always make me feel').",
        manipulation_score_analysis="High score due to clear manipulative phrases."
    ).with_inputs("transcript", "session_context"),
    dspy.Example(
        transcript="I understand your point, and I appreciate you sharing it. Let's find a solution together.",
        session_context="{}",
        is_manipulative=False,
        manipulation_score=0.1,
        manipulation_techniques=[],
        manipulation_explanation="The speaker is collaborative and respectful, showing no signs of manipulation.",
        manipulation_score_analysis="Low score due to positive, direct communication."
    ).with_inputs("transcript", "session_context"),
    dspy.Example(
        transcript="Everyone thinks you're being unreasonable. You're the only one who has a problem with this.",
        session_context="{}",
        is_manipulative=True,
        manipulation_score=0.7,
        manipulation_techniques=["Social pressure", "Minimization"],
        manipulation_explanation="Appeals to an alleged consensus ('Everyone thinks') and minimizes the listener's concerns.",
        manipulation_score_analysis="Score reflects social pressure tactics."
    ).with_inputs("transcript", "session_context"),
    dspy.Example(
        transcript="I've had such a terrible day, and now this... I just can't handle any more stress. Please, just do this one thing for me.",
        session_context="{}",
        is_manipulative=True,
        manipulation_score=0.6,
        manipulation_techniques=["Appeal to pity"],
        manipulation_explanation="The speaker is leveraging their bad day to elicit sympathy and compliance.",
        manipulation_score_analysis="Moderate score, as appeal to pity can be subtle but is present."
    ).with_inputs("transcript", "session_context"),
     dspy.Example(
        transcript="It's not a big deal, you're overreacting. I was just kidding.",
        session_context="{}",
        is_manipulative=True,
        manipulation_score=0.75,
        manipulation_techniques=["Minimization", "Gaslighting"],
        manipulation_explanation="The speaker downplays the listener's feelings and tries to make them doubt their reaction.",
        manipulation_score_analysis="Clear use of minimization and invalidation."
    ).with_inputs("transcript", "session_context")
]

# 3. Define Evaluation Metric Function
def simple_manipulation_metric(example, prediction, trace=None) -> float:
    """
    A simple metric focusing on the 'is_manipulative' flag and 'manipulation_techniques'.
    """
    # 'prediction' will be a dspy.Prediction object. Its attributes are the OutputFields from the signature.
    # 'example' is a dspy.Example object, its attributes are the labels.

    # Handle is_manipulative (prediction might be string "True"/"False" or boolean)
    pred_is_manipulative_str = str(getattr(prediction, "is_manipulative", "false")).lower()
    actual_is_manipulative = pred_is_manipulative_str == "true"

    label_is_manipulative = example.is_manipulative

    is_manipulative_match = actual_is_manipulative == label_is_manipulative

    # Handle manipulation_techniques (prediction is a JSON string list)
    pred_techniques_str = getattr(prediction, "manipulation_techniques", "[]")
    try:
        if isinstance(pred_techniques_str, list): # Already parsed by some chance (unlikely from raw LLM)
             parsed_prediction_techniques = [str(t).strip() for t in pred_techniques_str if str(t).strip()]
        elif isinstance(pred_techniques_str, str) and pred_techniques_str.strip():
            parsed_prediction_techniques = json.loads(pred_techniques_str)
            if not isinstance(parsed_prediction_techniques, list): # If JSON is not a list
                parsed_prediction_techniques = [str(parsed_prediction_techniques)]
            # Normalize to list of strings
            parsed_prediction_techniques = [str(t).strip() for t in parsed_prediction_techniques if str(t).strip()]
        else:
            parsed_prediction_techniques = []
    except json.JSONDecodeError:
        # If JSON parsing fails, treat as empty or try splitting if it's a simple comma-separated string
        if isinstance(pred_techniques_str, str) and ',' in pred_techniques_str:
            parsed_prediction_techniques = [t.strip() for t in pred_techniques_str.split(',') if t.strip()]
        else:
            parsed_prediction_techniques = []

    label_techniques_set = set(str(t).strip() for t in example.manipulation_techniques if str(t).strip())
    pred_techniques_set = set(parsed_prediction_techniques)

    techniques_match = pred_techniques_set == label_techniques_set

    # Basic scoring: 1.0 if both key fields match, 0.5 if one matches, 0.0 otherwise
    if is_manipulative_match and techniques_match:
        return 1.0
    elif is_manipulative_match or techniques_match:
        return 0.5
    else:
        return 0.0

# 4. Main Execution Block
if __name__ == "__main__":
    print(f"\nStarting DSPy optimization demo for {DSPyManipulationAnalyzer.__name__}...")

    # Optimizer Setup
    # max_bootstrapped_demos: Number of few-shot examples to generate.
    # max_labeled_demos: Number of labeled examples to use from trainset for bootstrapping.
    teleprompter = BootstrapFewShot(
        metric=simple_manipulation_metric,
        max_bootstrapped_demos=2, # Number of demos to include in the optimized prompt
        max_labeled_demos=len(trainset) # Use all training examples to find good demos
    )

    # Instantiate the uncompiled module
    uncompiled_manip_analyzer = DSPyManipulationAnalyzer()

    # Compile (optimize) the module
    # This will run the module on the trainset examples and use the metric
    # to find the best few-shot examples (demos) to improve performance.
    print("\nCompiling (optimizing) the module... This may take a few minutes...")
    try:
        optimized_manip_analyzer = teleprompter.compile(student=uncompiled_manip_analyzer, trainset=trainset)
        print("Compilation complete.")
    except Exception as e:
        print(f"Error during compilation: {e}")
        print("Skipping demonstration with optimized module due to compilation error.")
        # Fallback to only show uncompiled if compilation fails
        optimized_manip_analyzer = None


    # Test/Demonstrate
    print("\n--- Testing Modules ---")

    # Using one of the training examples as a test case for simplicity
    # In a real scenario, you'd use a separate dev/test set.
    test_example_index = 0
    test_example = trainset[test_example_index]
    test_transcript = test_example.transcript
    test_context_str = test_example.session_context # This is already a string "{}"

    print(f"\nTest Transcript:\n'{test_transcript}'")
    print(f"Expected is_manipulative: {test_example.is_manipulative}")
    print(f"Expected techniques: {test_example.manipulation_techniques}")

    # Get a prediction from the uncompiled module
    print("\n--- Uncompiled Module Prediction ---")
    try:
        # The DSPy module's forward method returns a Pydantic model.
        # For DSPy's internal Predict/ChainOfThought, it operates on the signature's OutputFields.
        # When calling the module directly, we get the Pydantic model.
        # For testing the optimization, we should look at the raw DSPy Prediction object if possible,
        # or simulate how `teleprompter.compile` calls the student.
        # The `student(example.inputs())` call inside compile will yield a dspy.Prediction.

        # To get raw dspy.Prediction for uncompiled:
        uncompiled_dspy_prediction = uncompiled_manip_analyzer.predictor(transcript=test_transcript, session_context=test_context_str)
        print(f"Raw is_manipulative: {getattr(uncompiled_dspy_prediction, 'is_manipulative', 'N/A')}")
        print(f"Raw manipulation_score: {getattr(uncompiled_dspy_prediction, 'manipulation_score', 'N/A')}")
        print(f"Raw manipulation_techniques: {getattr(uncompiled_dspy_prediction, 'manipulation_techniques', 'N/A')}")
        print(f"Raw manipulation_explanation: {getattr(uncompiled_dspy_prediction, 'manipulation_explanation', 'N/A')}")
        print(f"Raw manipulation_score_analysis: {getattr(uncompiled_dspy_prediction, 'manipulation_score_analysis', 'N/A')}")

        # Also show the Pydantic output for comparison
        uncompiled_pydantic_output = uncompiled_manip_analyzer.forward(transcript=test_transcript, session_context=json.loads(test_context_str))
        print(f"Pydantic is_manipulative: {uncompiled_pydantic_output.is_manipulative}")
        print(f"Pydantic techniques: {uncompiled_pydantic_output.manipulation_techniques}")

    except Exception as e:
        print(f"Error running uncompiled module: {e}")

    if optimized_manip_analyzer:
        # Get a prediction from the optimized module
        print("\n--- Optimized Module Prediction ---")
        try:
            # Similar to above, get raw dspy.Prediction for optimized module
            optimized_dspy_prediction = optimized_manip_analyzer.predictor(transcript=test_transcript, session_context=test_context_str)
            print(f"Raw is_manipulative: {getattr(optimized_dspy_prediction, 'is_manipulative', 'N/A')}")
            print(f"Raw manipulation_score: {getattr(optimized_dspy_prediction, 'manipulation_score', 'N/A')}")
            print(f"Raw manipulation_techniques: {getattr(optimized_dspy_prediction, 'manipulation_techniques', 'N/A')}")
            print(f"Raw manipulation_explanation: {getattr(optimized_dspy_prediction, 'manipulation_explanation', 'N/A')}")
            print(f"Raw manipulation_score_analysis: {getattr(optimized_dspy_prediction, 'manipulation_score_analysis', 'N/A')}")

            optimized_pydantic_output = optimized_manip_analyzer.forward(transcript=test_transcript, session_context=json.loads(test_context_str))
            print(f"Pydantic is_manipulative: {optimized_pydantic_output.is_manipulative}")
            print(f"Pydantic techniques: {optimized_pydantic_output.manipulation_techniques}")

            # Show the optimized prompt (demos)
            # For ChainOfThought, the demos are stored on the internal Predict module.
            # This internal Predict module is often named _predictor or is the first one in predictors list.
            print("\n--- Optimized Prompt Demos ---")
            internal_predictor = None
            if hasattr(optimized_manip_analyzer.predictor, '_predictor'): # Common internal name
                internal_predictor = optimized_manip_analyzer.predictor._predictor
            elif hasattr(optimized_manip_analyzer.predictor, 'predictors') and callable(optimized_manip_analyzer.predictor.predictors) and optimized_manip_analyzer.predictor.predictors(): # If it's a method returning a list
                predictors_list = optimized_manip_analyzer.predictor.predictors()
                if predictors_list:
                    internal_predictor = predictors_list[0]

            if internal_predictor and hasattr(internal_predictor, 'demos') and internal_predictor.demos:
                print(f"Found {len(internal_predictor.demos)} demos in the optimized predictor.")
                for i, demo in enumerate(internal_predictor.demos):
                    print(f"\nDemo {i+1}:")
                    # Printing the demo directly usually shows its fields.
                    # demo.inputs() or demo.labels() might fail if input_keys/label_keys aren't set on demo itself.
                    print(f"  Demo content: {demo}")
            else:
                print("No demos found in the optimized predictor's internal dspy.Predict module.")
        except Exception as e:
            print(f"Error running or inspecting optimized module: {e}") # Removed exc_info=True

    # Removing the global tracer history printout as it's not reliable for BootstrapFewShot's specific history.
    # BootstrapFewShot's process is reflected in the compiled module itself.
    print("\nOptimization demo script finished.")
