from typing import Optional
from typing import List,Optional
from sqlmodel import Field, SQLModel,Relationship

class Entreprise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True,index=True)
    name : str
    serveurs : str
    postes : str
    #serveur : list = Relationship(back_populates="entreprise")
    #host: List = Relationship(back_populates="entreprise")
    def __str__(self):
        return f"#{self.id} | Host {self.postes} d'ip {self.serveurs}"
    
    def __repr__(self):
        return f"<Host(id='{self.id}', name='{self.postes}', ip='{self.serveurs}')>"
