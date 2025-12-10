def test_prompt_scripts_exist():
    import os

    assert os.path.exists("src/experiments/eval_prompts.py")
