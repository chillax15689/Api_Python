from typing import Optional
from sqlmodel import Field, SQLModel

class Action(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    script_path: Optional[str] = Field(default=None)

    def exec_script(self) -> str:
        pass

    def __str__(self):
        return f"#{self.id} | Action {self.name} de script {self.script_path}"

    def __repr__(self):
        return f"<Action(id='{self.id}', name='{self.name}', script_path='{self.script_path}')>"
    
def main():
    a1 = Action(name="Memory Check", script_path="actions.memory_linux")
    print(a1)
    print(a1.exec_script())

if __name__ == "__main__":
    main()