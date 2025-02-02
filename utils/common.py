class CSource():
    def __init__(self, path: str) -> None:
        with open(path, 'r') as f:
            self.context = f.read()

    def _repr_html_(self) -> str:
        return "<pre class='code'><code class=\"cpp hljs\">" + self.context + "</code></pre>"

    def __str__(self) -> str:
        return f"```c\n{self.context}\n```"

    def __repr__(self) -> str:
        return str(self)