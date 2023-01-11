from behave import then


@then('an error "{error}" is raised')
def error(context, error: str):
    if not hasattr(context, "error"):
        assert False, "No error has been raised"
    assert str(context.error) == error, f"Got error: {context.error}"
