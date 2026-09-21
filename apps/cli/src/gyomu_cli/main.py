import typer

app = typer.Typer()

hello_app = typer.Typer()
app.add_typer(hello_app, name="hello")


# @hello_app.command()
@app.command()
def greet(name: str = "World") -> None:
    print(f"Hello, {name}!")


@app.command()
def greet2(name: str = "World") -> None:
    print(f"Hello, {name}!")


@hello_app.command("greet")
def greet3(name: str = "World") -> None:
    print(f"Hello, {name}!")


if __name__ == "__main__":
    app()
