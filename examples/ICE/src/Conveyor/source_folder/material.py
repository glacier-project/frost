class Material:
    def __init__(self, name:str, barcode:int, height:int, length:int, width:int):
        self.barcode:int = barcode
        self.name:str = name        
        self.height:int = height
        self.length:int = length
        self.width:int = width