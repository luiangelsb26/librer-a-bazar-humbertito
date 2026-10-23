"""Generación de informes PDF de diagnóstico de demanda e inventario."""

from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape


def construir_informe_prediccion(datos):
    """Devuelve un PDF con el pronóstico, su validación y recomendaciones."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
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
    gris = colors.HexColor("#52616B")
    gris_claro = colors.HexColor("#EEF3F5")
    borde = colors.HexColor("#D5E0E4")

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="Diagnóstico de demanda y recomendación de inventario",
        author="Sistema Librería Bazar Humbertito",
    )
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        name="TituloInforme",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=azul,
        alignment=TA_CENTER,
        spaceAfter=5,
    ))
    estilos.add(ParagraphStyle(
        name="SubtituloInforme",
        parent=estilos["Normal"],
        fontSize=9,
        leading=13,
        textColor=gris,
        alignment=TA_CENTER,
        spaceAfter=12,
    ))
    estilos.add(ParagraphStyle(
        name="SeccionInforme",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=azul,
        spaceBefore=9,
        spaceAfter=5,
    ))
    estilos.add(ParagraphStyle(
        name="TextoInforme",
        parent=estilos["BodyText"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#26343D"),
        spaceAfter=5,
    ))
    estilos.add(ParagraphStyle(
        name="NotaInforme",
        parent=estilos["BodyText"],
        fontSize=8,
        leading=11,
        textColor=gris,
    ))

    def texto(valor):
        return Paragraph(escape(str(valor)), estilos["TextoInforme"])

    def tabla(datos_tabla, anchos, encabezado=True):
        estilo_encabezado = ParagraphStyle(
            "EncabezadoTabla",
            parent=estilos["TextoInforme"],
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )
        celdas = []
        for indice_fila, fila in enumerate(datos_tabla):
            estilo_celda = estilo_encabezado if encabezado and indice_fila == 0 else estilos["TextoInforme"]
            celdas.append([
                Paragraph(escape(str(celda)), estilo_celda)
                for celda in fila
            ])
        tabla_pdf = Table(celdas, colWidths=anchos, repeatRows=1 if encabezado else 0)
        reglas = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.45, borde),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
        if encabezado:
            reglas.extend([
                ("BACKGROUND", (0, 0), (-1, 0), azul),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
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
    sugerida = int(datos.get("cantidad_sugerida") or 0)
    periodo = datos.get("periodo", "No disponible")

    if sugerida > 0 and stock <= minimo:
        diagnostico = (
            "El stock actual está en el mínimo configurado o por debajo de este. "
            "La proyección también indica una necesidad de reposición; priorice la revisión."
        )
    elif sugerida > 0:
        diagnostico = (
            "Con la demanda proyectada y el stock mínimo configurado, se estima "
            "una necesidad de reposición. Valide la cantidad sugerida antes de comprar."
        )
    elif demanda > 0:
        diagnostico = (
            "Según la proyección, el stock actual cubre la demanda estimada del periodo "
            "y conserva el mínimo configurado. Mantenga el seguimiento del inventario."
        )
    else:
        diagnostico = (
            "No se proyectan unidades vendidas para el periodo seleccionado. "
            "Revise el historial y la disponibilidad del producto antes de tomar decisiones."
        )

    recomendaciones = []
    if sugerida > 0:
        recomendaciones.append(
            f"Evaluar la reposición de aproximadamente {sugerida} unidad(es), "
            "considerando la demanda proyectada y el stock mínimo."
        )
    else:
        recomendaciones.append(
            "No se sugiere una reposición inmediata según esta proyección; "
            "seguir revisando las ventas y el stock."
        )
    recomendaciones.append(
        "Confirmar que no hubo quiebres de stock, cierres o días sin registro "
        "que puedan distorsionar la demanda observada."
    )
    recomendaciones.append(
        "Usar este informe como apoyo para la revisión gerencial; validar la compra "
        "con disponibilidad, presupuesto y criterio del responsable."
    )

    historia = [
        Paragraph("Librería Bazar Humbertito", estilos["SubtituloInforme"]),
        Paragraph("Diagnóstico de demanda y recomendación de inventario", estilos["TituloInforme"]),
        Paragraph(f"Informe generado por el sistema · {escape(fecha_emision)}", estilos["SubtituloInforme"]),
        Paragraph("1. Identificación del análisis", estilos["SeccionInforme"]),
        tabla([
            ["Producto", "Código", "Periodo proyectado"],
            [datos.get("nombre_producto", "No disponible"), datos.get("codigo_producto", "No disponible"), periodo],
        ], [65 * mm, 38 * mm, 71 * mm]),
        Spacer(1, 5),
        tabla([
            ["Historial disponible", "Última venta registrada", "Fecha de corte"],
            [
                f"{int(datos.get('dias_historicos') or 0)} días",
                datos.get("fecha_ultima_venta", "No disponible"),
                datos.get("fecha_base", "No disponible"),
            ],
        ], [58 * mm, 58 * mm, 58 * mm]),
        Paragraph("2. Resultado del pronóstico", estilos["SeccionInforme"]),
        tabla([
            ["Demanda estimada", "Promedio diario", "Stock actual", "Stock mínimo"],
            [
                f"{demanda:.2f} unidades",
                f"{promedio:.2f} unidades",
                f"{stock:.0f}",
                f"{minimo:.0f}",
            ],
        ], [43 * mm, 43 * mm, 43 * mm, 43 * mm]),
        Paragraph("3. Diagnóstico", estilos["SeccionInforme"]),
        texto(diagnostico),
    ]

    if filas_periodo:
        historia.extend([
            Paragraph("Detalle diario estimado", estilos["SeccionInforme"]),
            tabla([["Fecha", "Unidades estimadas"], *filas_periodo], [90 * mm, 82 * mm]),
        ])

    historia.extend([
        Paragraph("4. Proceso aplicado", estilos["SeccionInforme"]),
        tabla([
            ["Etapa", "Descripción"],
            ["Preparación", "Se organizó el historial de ventas por producto y fecha."],
            ["Evaluación", "Se reservaron fechas recientes para comparar el pronóstico con las ventas observadas."],
            ["Referencia", "Se contrastó el error con una referencia basada en las ventas de siete días antes."],
            ["Resultado", "El pronóstico se habilita cuando su error de evaluación es menor que el de la referencia."],
        ], [35 * mm, 137 * mm]),
    ])

    if evaluacion:
        mae_modelo = evaluacion.get("mae")
        mae_referencia = evaluacion.get("mae_baseline_7_dias")
        estado_comparacion = "No disponible"
        if mae_modelo is not None and mae_referencia is not None:
            estado_comparacion = (
                "Menor error que la referencia"
                if mae_modelo < mae_referencia
                else "No superó la referencia"
            )
        historia.extend([
            Paragraph("5. Verificación de la evaluación", estilos["SeccionInforme"]),
            tabla([
                ["Indicador", "Resultado"],
                ["Error medio absoluto de evaluación (todos los productos)", f"{mae_modelo:.2f} unidades por producto y día" if mae_modelo is not None else "No disponible"],
                ["Error de la referencia de siete días", f"{mae_referencia:.2f} unidades" if mae_referencia is not None else "No disponible"],
                ["Resultado comparativo", estado_comparacion],
                ["Fechas evaluadas", f"{evaluacion.get('fecha_inicio_prueba', 'No disponible')} a {evaluacion.get('fecha_fin_prueba', 'No disponible')}"],
                ["Observaciones de prueba", str(evaluacion.get("observaciones_prueba", "No disponible"))],
            ], [76 * mm, 96 * mm]),
        ])
    else:
        historia.extend([
            Paragraph("5. Verificación de la evaluación", estilos["SeccionInforme"]),
            texto("No hay métricas de evaluación disponibles en el registro del pronóstico."),
        ])

    historia.extend([
        Paragraph("6. Recomendaciones", estilos["SeccionInforme"]),
        tabla([["N.º", "Recomendación"]] + [
            [str(indice), recomendacion]
            for indice, recomendacion in enumerate(recomendaciones, start=1)
        ], [15 * mm, 157 * mm]),
        Spacer(1, 8),
        Paragraph(
            "Alcance: el pronóstico y la recomendación describen una evaluación operativa "
            "del sistema. No demuestran por sí solos una mejora en la toma de decisiones "
            "gerenciales ni sustituyen la revisión del responsable. Los días sin ventas "
            "registradas se interpretan como cero; un quiebre de stock puede hacer que la "
            "demanda real sea mayor que la observada.",
            estilos["NotaInforme"],
        ),
    ])

    def pie_pagina(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(borde)
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(gris)
        canvas.drawString(18 * mm, 9 * mm, "Sistema Librería Bazar Humbertito")
        canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Página {doc.page}")
        canvas.restoreState()

    documento.build(historia, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
    return buffer.getvalue()
