# aqua_manager/src/AquaKeeper/patrones/factory/producto_factory.py
from AquaKeeper.entidades.modelo import Producto

class ProductoFactory:
    @staticmethod
    def _crear_cloro_granulado(sku: str, nombre: str, presentacion: str="1kg") -> Producto:
        return Producto(sku, nombre, "cloro-granulado", "g", presentacion)

    @staticmethod
    def _crear_cloro_pastilla(sku: str, nombre: str, presentacion: str="200g") -> Producto:
        return Producto(sku, nombre, "cloro-pastilla", "pastillas", presentacion)

    @staticmethod
    def _crear_clarificador(sku: str, nombre: str, presentacion: str="1L") -> Producto:
        return Producto(sku, nombre, "clarificador", "ml", presentacion)

    @staticmethod
    def _crear_alguicida(sku: str, nombre: str, presentacion: str="1L") -> Producto:
        return Producto(sku, nombre, "alguicida", "ml", presentacion)

    @staticmethod
    def _crear_antisarro(sku: str, nombre: str, presentacion: str="1L") -> Producto:
        return Producto(sku, nombre, "antisarro", "ml", presentacion)

    @staticmethod
    def crear(tipo: str, sku: str, nombre: str, presentacion: str="") -> Producto:
        dispatch = {
            "cloro-granulado": ProductoFactory._crear_cloro_granulado,
            "cloro-pastilla":  ProductoFactory._crear_cloro_pastilla,
            "clarificador":    ProductoFactory._crear_clarificador,
            "alguicida":       ProductoFactory._crear_alguicida,
            "antisarro":       ProductoFactory._crear_antisarro,
        }
        key = (tipo or "").lower()
        if key not in dispatch:
            raise ValueError(f"Tipo de producto desconocido: {tipo}")
        return dispatch[key](sku, nombre, presentacion or "")
