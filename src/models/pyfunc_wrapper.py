# src/model/pyfunc_wrapper.py
import mlflow.pyfunc
import pandas as pd
from .chroma_model import analyze_image


class ChromaMatchPyFunc(mlflow.pyfunc.PythonModel):
    def load_context(self, context) -> None:
        # no extra artifacts required; chroma_model will lazy-load HF model when called
        pass

    def predict(self, context, model_input: pd.DataFrame) -> pd.DataFrame:
        """
        model_input: pandas DataFrame with a column 'image_path' containing local paths to images.
        Returns a DataFrame with a column 'result' which is the dictionary produced by analyze_image.
        """
        if isinstance(model_input, dict):
            # single-row dict
            image_paths = [model_input.get("image_path")]
        else:
            image_paths = list(model_input["image_path"].values)

        results = []
        for p in image_paths:
            res = analyze_image(p)
            results.append(res)
        return pd.DataFrame({"result": results})
