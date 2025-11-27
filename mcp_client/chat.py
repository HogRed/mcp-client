async def run_chat(handler) -> None:
    """Run an AI-handled chat session."""

    print("\nMCP Client's Chat Started!")
    print("Type your queries or 'quit' to exit.")

    # Chat loop
    while True:
        try:
            # Get user input
            if not (query := input("\nYou: ").strip()):
                continue

            # Exit condition
            if query.lower() == "quit":
                break
            # Process the query and print the response
            print("\n" + await handler.process_query(query))
        # Handle keyboard interrupt gracefully
        except Exception as e:
            print(f"\nError: {str(e)}")

    print("\nGoodbye!")