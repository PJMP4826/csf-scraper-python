from pydantic import BaseModel, Field


class RfcCifSchema(BaseModel):
    """Datos que el LLM debe devolver de una imagen de Constancia de Situación Fiscal (CSF).

    Se usa como ``output_cls`` del programa multimodal de LlamaIndex, que
    adjunta automáticamente al prompt el JSON Schema de esta clase.
    """

    rfc: str = Field(
        min_length=1,
        description=(
            "Registro Federal de Contribuyentes (RFC) de la persona física o moral. "
            "Ubicación en la imagen:\n"
            "1. En el renglón 'RFC:' de la sección 'Datos de Identificación del "
            "Contribuyente'.\n"
            "2. Arriba del texto 'Registro Federal de Contribuyentes', a la derecha "
            "del código QR.\n"
            "3. Debajo del código de barras vertical del lado derecho del encabezado.\n"
            "Formato: Cadena alfanumérica en mayúsculas de 12 caracteres (persona moral) o 13 "
            "caracteres (persona física) sin espacios, guiones ni puntos.\n"
            "Ejemplos válidos: 'SME2009297K7', 'MEPF050926N61', 'TME990513J64'."
        ),
    )
    id_cif: str = Field(
        min_length=1,
        description=(
            "Identificador de la Cédula de Identificación Fiscal (idCIF).\n"
            "Ubicación en la imagen:\n"
            "Se encuentra EXCLUSIVAMENTE dentro del recuadro de la 'CÉDULA DE "
            "IDENTIFICACIÓN FISCAL' "
            "(a la derecha del código QR), sobre la leyenda 'VALIDA TU INFORMACIÓN FISCAL', "
            "antecedido por la etiqueta 'idCIF:'.\n"
            "Formato: Extraer ÚNICAMENTE los números (de 8 a 13 dígitos consecutivos), "
            "omitiendo el prefijo 'idCIF:', espacios, guiones o cualquier otro carácter.\n"
            "Ejemplos válidos:\n"
            "- Si dice 'idCIF: 20090374035', extraer únicamente '20090374035'.\n"
            "- Si dice 'idCIF: 25020218873', extraer únicamente '25020218873'.\n"
            "- Si dice 'idCIF: 15080334415', extraer únicamente '15080334415'."
        ),
    )
