CSF_PROMPT = (
    "Analiza la imagen adjunta, que es una Constancia de Situación Fiscal "
    "emitida por el SAT, y extrae el RFC y el idCIF que aparecen en el "
    "encabezado del documento. Transcribe ambos valores exactamente como están "
    "impresos: conserva las mayúsculas, el signo & y la Ñ si aparecen, y no "
    "elimines los ceros a la izquierda del idCIF. No inventes ni completes "
    "valores: si un dato no se distingue en la imagen, devuélvelo como cadena "
    "vacía."
)

#: Sufijo que se agrega al prompt cuando el intento anterior fue rechazado.
RETRY_PROMPT = (
    "\n\nATENCIÓN: el intento #{previous_attempt} fue descartado por este "
    "motivo:\n{error}\n\n"
    "Vuelve a revisar la imagen con cuidado, carácter por carácter, y corrige "
    "exactamente eso antes de responder."
)
