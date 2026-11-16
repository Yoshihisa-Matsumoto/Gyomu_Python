from pydantic import BaseModel, ConfigDict


class TextEditorConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    command: str


VSCODE_SETTING = TextEditorConfig(
    name="VS Code", command="code --reuse-window --wait ##FILENAME##"
)
