"""Genera el informe operativo de pronóstico y diagnóstico de inventario."""

from datetime import datetime
from io import BytesIO
from math import ceil
from xml.sax.saxutils import escape


def construir_informe_prediccion(datos):
    """Devuelve un PDF de diagnóstico para una predicción completada."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    buffer = BytesIO()
    azul = colors.HexColor("#15344A")
    turquesa = colors.HexColor("#278C83")
    verde_claro = colors.HexColor("#E6F4F0")
    gris = colors.HexColor("#53636E")
    gris_claro = colors.HexColor("#F1F5F7")
    borde = colors.HexColor("#D5E0E4")
    texto_oscuro = colors.HexColor("#243640")

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=24 * mm,
        bottomMargin=17 * mm,
        title="Informe de pronóstico y diagnóstico de inventario",
        author="Sistema Librería Bazar Humbertito",
    )
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        name="TituloInforme",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        textColor=azul,
        alignment=TA_LEFT,
        spaceAfter=4,
    ))
    estilos.add(ParagraphStyle(
        name="MarcaInforme",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=turquesa,
        spaceAfter=3,
    ))
    estilos.add(ParagraphStyle(
        name="MetaInforme",
        parent=estilos["Normal"],
        fontSize=8,
        leading=11,
        textColor=gris,
    ))
    estilos.add(ParagraphStyle(
        name="SeccionInforme",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=azul,
        spaceBefore=9,
        spaceAfter=5,
        keepWithNext=True,
    ))
    estilos.add(ParagraphStyle(
        name="TextoInforme",
        parent=estilos["BodyText"],
        fontSize=8.5,
        leading=12,
        textColor=texto_oscuro,
        spaceAfter=3,
    ))
    estilos.add(ParagraphStyle(
        name="TextoBlancoInforme",
        parent=estilos["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    ))
    estilos.add(ParagraphStyle(
        name="EtiquetaInforme",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=gris,
    ))
    estilos.add(ParagraphStyle(
        name="ValorInforme",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=azul,
    ))
    estilos.add(ParagraphStyle(
        name="EstadoInforme",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#176B5D"),
        alignment=TA_CENTER,
    ))

    def p(valor, estilo="TextoInforme"):
        return Paragraph(escape(str(valor)), estilos[estilo])

    def tabla(filas, anchos, encabezado=True, encabezado_color=azul):
        celdas = []
        for indice, fila in enumerate(filas):
            estilo_celda = "TextoBlancoInforme" if encabezado and indice == 0 else "TextoInforme"
            celdas.append([
                celda if isinstance(celda, Paragraph) else p(celda, estilo_celda)
                for celda in fila
            ])
        tabla_pdf = Table(
            celdas,
            colWidths=anchos,
            repeatRows=1 if encabezado else 0,
            hAlign="LEFT",
        )
        reglas = [
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.45, borde),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
        if encabezado:
            reglas.extend([
                ("BACKGROUND", (0, 0), (-1, 0), encabezado_color),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, gris_claro]),
            ])
        else:
            reglas.append(("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, gris_claro]))
        tabla_pdf.setStyle(TableStyle(reglas))
        return tabla_pdf

    fecha_emision = datos.get("fecha_emision") or datetime.now().strftime("%d/%m/%Y %H:%M")
    filas_periodo = datos.get("filas_prediccion", [])
    evaluacion = datos.get("evaluacion") or {}
    demanda = float(datos.get("demanda_predicha") or 0)
    promedio = float(datos.get("promedio_diario") or 0)
    stock = float(datos.get("stock_actual") or 0)
    minimo = float(datos.get("stock_minimo") or 0)
    sugerida = max(0, int(datos.get("cantidad_sugerida") or 0))
    periodo = datos.get("periodo", "No disponible")
    necesidad_neta = demanda + minimo - stock

    if sugerida > 0 and stock <= minimo:
        diagnostico = (
            "El stock actual está en el mínimo configurado o por debajo. "
            "La proyección también identifica una necesidad de reposición, por lo que "
            "conviene priorizar su revisión."
        )
        nivel = "Revisión prioritaria"
    elif sugerida > 0:
        diagnostico = (
            "El stock actual no cubriría simultáneamente la demanda proyectada y el "
            "stock mínimo configurado. Se estima una cantidad de reposición para "
            "revisar antes de emitir una compra."
        )
        nivel = "Revisar reposición"
    elif demanda > 0:
        diagnostico = (
            "El stock actual cubre la demanda proyectada del periodo y conserva el "
            "mínimo configurado. Se recomienda continuar el seguimiento."
        )
        nivel = "Cobertura suficiente"
    else:
        diagnostico = (
            "No se proyectan unidades vendidas para el periodo. Revise el historial "
            "y la disponibilidad del producto para descartar falta de registros o "
            "quiebres de stock."
        )
        nivel = "Revisar historial"

    mae = evaluacion.get("mae")
    mae_referencia = evaluacion.get("mae_baseline_7_dias")
    wape = evaluacion.get("wape_porcentaje")
    evaluacion_superada = (
        mae is not None
        and mae_referencia is not None
        and float(mae) < float(mae_referencia)
    )
    estado_evaluacion = (
        "Superó la referencia" if evaluacion_superada
        else "No disponible" if mae is None or mae_referencia is None
        else "No superó la referencia"
    )

    recomendaciones = []
    if sugerida > 0:
        recomendaciones.append(
            f"Evaluar la reposición de {sugerida} unidad(es), de acuerdo con la "
            "demanda proyectada y el stock mínimo configurado."
        )
    else:
        recomendaciones.append(
            "No se estima reposición inmediata con los datos actuales; mantener el "
            "seguimiento del stock y de las ventas."
        )
    recomendaciones.append(
        "Verificar que el producto estuvo disponible durante el periodo: las ventas "
        "registradas pueden subestimar la demanda si hubo quiebre de stock."
    )
    recomendaciones.append(
        "Contrastar la sugerencia con el plazo del proveedor, presupuesto y ritmo "
        "de reposición antes de emitir una compra."
    )

    ancho_util = A4[0] - 34 * mm
    historia = [
        p("Librería Bazar Humbertito", "MarcaInforme"),
        p("Informe de pronóstico y diagnóstico de inventario", "TituloInforme"),
        p(f"Generado el {fecha_emision} · Estado de esta ejecución: COMPLETADA", "MetaInforme"),
        Spacer(1, 7),
        tabla([
            ["DIAGNÓSTICO PRINCIPAL", "NIVEL DE ATENCIÓN"],
            [p(diagnostico), p(nivel, "EstadoInforme")],
        ], [124 * mm, ancho_util - 124 * mm], encabezado=True, encabezado_color=turquesa),
        Paragraph("1. Comprobaciones realizadas por el sistema", estilos["SeccionInforme"]),
        tabla([
            ["Comprobación", "Resultado", "Estado"],
            ["Historial del producto", f"{int(datos.get('dias_historicos') or 0)} días calendario procesados", "Completado"],
            ["Evaluación temporal", "Pronóstico comparado con una referencia de siete días", estado_evaluacion],
            ["Periodo futuro", periodo, "Calculado"],
            ["Inventario", "Stock actual contrastado con stock mínimo y demanda estimada", "Evaluado"],
            ["Recomendación", "Necesidad de reposición calculada para este producto", "Generada"],
        ], [42 * mm, 93 * mm, 39 * mm]),
        Paragraph("2. Identificación y datos del producto", estilos["SeccionInforme"]),
        tabla([
            ["Producto", "Código", "Última venta registrada"],
            [
                datos.get("nombre_producto", "No disponible"),
                datos.get("codigo_producto", "No disponible"),
                datos.get("fecha_ultima_venta", "No disponible"),
            ],
            ["Periodo pronosticado", "Fecha de corte del historial", "Días de historial"],
            [
                periodo,
                datos.get("fecha_base", "No disponible"),
                str(int(datos.get("dias_historicos") or 0)),
            ],
        ], [65 * mm, 55 * mm, ancho_util - 120 * mm]),
        Paragraph("3. Resultado del pronóstico e inventario", estilos["SeccionInforme"]),
        tabla([
            ["Demanda total estimada", "Promedio diario", "Stock actual", "Stock mínimo"],
            [
                f"{demanda:.2f} unidades",
                f"{promedio:.2f} unidades/día",
                f"{stock:.0f} unidades",
                f"{minimo:.0f} unidades",
            ],
        ], [43.5 * mm] * 4),
        Spacer(1, 4),
        p(
            "Cálculo de reposición: máximo entre cero y el techo de "
            "(demanda estimada + stock mínimo - stock actual). "
            f"Aplicado a este caso: máximo(0, techo({demanda:.10f} + "
            f"{minimo:.0f} - {stock:.0f})) = {sugerida} unidad(es)."
        ),
    ]

    if filas_periodo:
        historia.extend([
            Paragraph("4. Detalle diario de la demanda estimada", estilos["SeccionInforme"]),
            tabla([["Fecha", "Unidades estimadas"], *filas_periodo], [90 * mm, ancho_util - 90 * mm]),
        ])

    historia.extend([
        Paragraph("5. Cómo se obtuvo el resultado", estilos["SeccionInforme"]),
        tabla([
            ["Etapa", "Descripción del proceso"],
            ["Preparación de datos", "Se agruparon las ventas por producto y fecha; los días sin registros se procesaron como cero ventas."],
            ["Evaluación", "Se separaron fechas recientes para medir el error del pronóstico sobre datos no usados en ese tramo de entrenamiento."],
            ["Comparación", "El error se contrastó con una referencia que repite las ventas observadas siete días antes."],
            ["Activación", "El pronóstico se habilita cuando la evaluación registra menor error que la referencia."],
        ], [39 * mm, ancho_util - 39 * mm]),
        Paragraph("6. Resultado de la evaluación temporal", estilos["SeccionInforme"]),
    ])

    if evaluacion:
        filas_evaluacion = [
            ["Indicador", "Resultado"],
            ["Error medio absoluto del sistema (MAE)", f"{float(mae):.2f} unidades por producto y día" if mae is not None else "No disponible"],
            ["Error de referencia (ventas de hace siete días)", f"{float(mae_referencia):.2f} unidades por producto y día" if mae_referencia is not None else "No disponible"],
            ["Comparación", estado_evaluacion],
            ["Fechas de prueba", f"{evaluacion.get('fecha_inicio_prueba', 'No disponible')} al {evaluacion.get('fecha_fin_prueba', 'No disponible')}"],
            ["Observaciones evaluadas", str(evaluacion.get("observaciones_prueba", "No disponible"))],
        ]
        if wape is not None:
            filas_evaluacion.append(["WAPE del sistema", f"{float(wape):.1f}%"])
        historia.append(tabla(filas_evaluacion, [83 * mm, ancho_util - 83 * mm]))
    else:
        historia.append(p("No se encontraron métricas de evaluación en el registro del pronóstico."))

    historia.extend([
        Paragraph("7. Recomendaciones de gestión", estilos["SeccionInforme"]),
        tabla([["N.º", "Acción recomendada"]] + [
            [str(indice), recomendacion]
            for indice, recomendacion in enumerate(recomendaciones, start=1)
        ], [14 * mm, ancho_util - 14 * mm]),
    ])

    def pie_pagina(canvas, doc):
        canvas.saveState()
        if doc.page > 1:
            canvas.setFont("Helvetica-Bold", 8)
            canvas.setFillColor(azul)
            canvas.drawString(17 * mm, A4[1] - 13 * mm, "Librería Bazar Humbertito")
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(gris)
            canvas.drawRightString(
                A4[0] - 17 * mm,
                A4[1] - 13 * mm,
                "Informe de pronóstico y diagnóstico de inventario",
            )
            canvas.setStrokeColor(borde)
            canvas.line(17 * mm, A4[1] - 17 * mm, A4[0] - 17 * mm, A4[1] - 17 * mm)
        canvas.setStrokeColor(borde)
        canvas.setLineWidth(0.6)
        canvas.line(17 * mm, 13 * mm, A4[0] - 17 * mm, 13 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(gris)
        canvas.drawString(17 * mm, 8 * mm, "Librería Bazar Humbertito · Informe de uso interno")
        canvas.drawRightString(A4[0] - 17 * mm, 8 * mm, f"Página {doc.page}")
        canvas.restoreState()

    documento.build(historia, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
    return buffer.getvalue()
