from guardrails import Guard

rail_path = "rails/content_safety.rail"
guard = Guard.for_rail(rail_path)


def run_with_guardrails(rag_function, user_query: str):
    """
    rag_function: your existing function that generates an answer
    user_query: query from the user
    """

    # # Step 1: validate input
    # validated_input = guard.parse(
    #     input_vars={"user_query": user_query},
    #     llm_output="",  # we haven't generated anything yet
    #     prompt="Validate only.",
    # )

    # # If input fails validation, stop early
    # if validated_input.validation_passed:
    #     raise ValueError(
    #         f"Input failed guardrails validation: {validated_input.raw_llm_output}"
    #     )

    # Step 2: run RAG AFTER input passes
    rag_output = rag_function(user_query)

    # Step 3: validate output
    validated_output = guard.parse(
        input_vars={"user_query": user_query},
        llm_output=rag_output["rag_answer"],
        prompt="Validate output.",
    )

    if validated_output.validation_passed is True:
        rag_output["rag_answer"] = validated_output.validated_output
    else:
        rag_output["rag_answer"] = validated_output.raw_llm_output

    return rag_output
