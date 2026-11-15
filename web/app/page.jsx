'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  BookOpen, ChartNoAxesCombined, ChartNoAxesColumnIncreasing, CircleAlert, Eye, EyeOff, LogIn,
  LayoutDashboard, LogOut, Menu, Package, ReceiptText, Search, ShoppingCart,
  TrendingUp, UsersRound,
} from 'lucide-react';
import Script from 'next/script';

const navigation = [
  ['Resumen', [['resumen', 'Vista general', 'dashboard']]],
  ['Operaciones', [
    ['productos', 'Inventario', 'inventory_2'],
    ['ventas', 'Ventas', 'point_of_sale'],
    ['compras', 'Compras', 'shopping_cart'],
  ]],
  ['Análisis', [
    ['analisis', 'Análisis comercial', 'monitoring'],
    ['modelo', 'Pronóstico', 'trending_up'],
  ]],
  ['Gestión', [['usuarios', 'Administración', 'manage_accounts']]],
];
const sections = navigation.flatMap(([, entries]) => entries);
const money = new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' });
const integer = new Intl.NumberFormat('es-PE', { maximumFractionDigits: 2 });
const localDay = new Intl.DateTimeFormat('sv-SE', { timeZone: 'America/Lima' });
const movementColumns = [
  ['id', 'N.º'], ['fecha', 'Fecha'], ['referencia', 'Comprobante'], ['producto', 'Producto'],
  ['cantidad', 'Unidades'], ['precio', 'Precio unitario', 'money'], ['subtotal', 'Subtotal', 'money'],
];

async function call(path, body) {
  const post = body !== undefined;
  const upload = body instanceof FormData;
  const response = await fetch('/api/' + path, {
    cache: 'no-store',
    method: post ? 'POST' : 'GET',
    headers: post ? {
      'X-Humbertito-Request': '1',
      ...(!upload && { 'Content-Type': 'application/json' }),
    } : undefined,
    body: post ? (upload ? body : JSON.stringify(body)) : undefined,
  });
  const data = await response.json().catch(() => null);
  if (!response.ok || data === null) {
    const error = new Error(data?.message ?? 'No se pudo conectar con el sistema.');
    error.status = response.status;
    error.details = data?.errors;
    throw error;
  }
  return data;
}

const icons = {
  dashboard: LayoutDashboard, inventory_2: Package, point_of_sale: ReceiptText,
  shopping_cart: ShoppingCart, monitoring: ChartNoAxesCombined, trending_up: TrendingUp,
  manage_accounts: UsersRound, search: Search, warning: CircleAlert, show_chart: ChartNoAxesCombined,
  query_stats: ChartNoAxesColumnIncreasing, menu_book: BookOpen, menu: Menu, logout: LogOut,
};

function Icon({ name }) {
  const Glyph = icons[name];
  return Glyph ? <Glyph className="icon" size={20} strokeWidth={1.8} aria-hidden="true"/> : null;
}

function Notice({ message, error = false }) {
  if (!message) return null;
  return <div className={'notice ' + (error ? 'error' : '')} role={error ? 'alert' : 'status'}>{message}</div>;
}

function Field({ label, children }) {
  return <label className="field"><span>{label}</span>{children}</label>;
}

function Card({ title, actions, children }) {
  return <section className="card"><div className="card-heading"><h2>{title}</h2>{actions}</div>{children}</section>;
}

function Table({ rows = [], columns, action, searchable = false }) {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const filtered = useMemo(() => {
    const term = search.trim().toLocaleLowerCase('es');
    return term ? rows.filter(row => columns.some(([key]) => String(row[key] ?? '').toLocaleLowerCase('es').includes(term))) : rows;
  }, [rows, columns, search]);
  const pageSize = 12;
  const last = Math.max(0, Math.ceil(filtered.length / pageSize) - 1);
  const current = Math.min(last, page);
  return <>
    {searchable && <label className="search"><Icon name="search"/><input aria-label="Buscar registros" placeholder="Buscar registros…" value={search} onChange={e => { setSearch(e.target.value); setPage(0); }}/></label>}
    {!filtered.length ? <p className="empty">No hay registros para mostrar.</p> :
      <div className="table-wrap"><table><thead><tr>
        {columns.map(([key, label]) => <th key={key} scope="col">{label}</th>)}{action && <th scope="col">Acciones</th>}
      </tr></thead><tbody>
        {filtered.slice(current * pageSize, (current + 1) * pageSize).map((row, i) => <tr key={row.linea ?? (row.id + '-' + i)}>
          {columns.map(([key, , format]) => <td key={key}>
            {row[key] == null ? '—' : format === 'money' ? money.format(row[key]) : key === 'stock' ?
              <span className={Number(row.stock) <= Number(row.stock_minimo) ? 'pill warning' : 'pill'}>{row.stock}</span> : String(row[key])}
          </td>)}
          {action && <td className="row-actions">{action(row)}</td>}
        </tr>)}
      </tbody></table></div>
    }
    {filtered.length > pageSize && <div className="pagination"><span>{filtered.length} registros · Página {current + 1} de {last + 1}</span><div>
      <button type="button" disabled={!current} onClick={() => setPage(current - 1)}>Anterior</button>
      <button type="button" disabled={current === last} onClick={() => setPage(current + 1)}>Siguiente</button>
    </div></div>}
  </>;
}

function objectTable(rows) {
  const list = Array.isArray(rows) ? rows : [];
  const keys = Object.keys(list[0] ?? {});
  return <Table rows={list} columns={keys.map(key => [key, key.replaceAll('_', ' ')])}/>;
}

function Metrics({ items }) {
  return <div className="metrics">
    {items.map(([label, value, icon]) => <article className="metric" key={label}>
      {icon && <span className="metric-icon"><Icon name={icon}/></span>}<span>{label}</span><strong>{value ?? '—'}</strong>
    </article>)}
  </div>;
}

const axisAmount = new Intl.NumberFormat('es-PE', {
  style: 'currency', currency: 'PEN', minimumFractionDigits: 0, maximumFractionDigits: 2,
});

function SalesPlot({ rows, max, selectedDay }) {
  const canvas = useRef(null);

  useEffect(() => {
    const chart = canvas.current;
    const context = chart.getContext('2d');
    if (!context) return;

    function draw() {
      const { width, height } = chart.getBoundingClientRect();
      if (!width || !height) return;
      const ratio = window.devicePixelRatio || 1;
      chart.width = Math.round(width * ratio);
      chart.height = Math.round(height * ratio);
      context.setTransform(ratio, 0, 0, ratio, 0, 0);

      const points = rows.map(({ day, value }, index) => ({
        day,
        x: (index + .5) * width / rows.length,
        y: Math.max(5, Math.min(height - 5, height * (1 - value / max))),
      }));
      const first = points[0];
      const last = points.at(-1);
      const accent = '#c1a3ff';
      const gradient = context.createLinearGradient(0, 0, 0, height);
      gradient.addColorStop(0, '#a986f55c');
      gradient.addColorStop(1, '#a986f506');

      function trace() {
        context.moveTo(first.x, first.y);
        for (const point of points.slice(1)) context.lineTo(point.x, point.y);
      }

      context.beginPath();
      trace();
      context.lineTo(last.x, height);
      context.lineTo(first.x, height);
      context.closePath();
      context.fillStyle = gradient;
      context.fill();

      const active = points.find(point => point.day === selectedDay);
      if (active) {
        context.beginPath();
        context.moveTo(active.x, 0);
        context.lineTo(active.x, height);
        context.strokeStyle = '#c1a3ff69';
        context.lineWidth = 1;
        context.setLineDash([4, 4]);
        context.stroke();
        context.setLineDash([]);
      }

      context.beginPath();
      trace();
      context.strokeStyle = accent;
      context.lineJoin = 'round';
      context.lineCap = 'round';
      context.lineWidth = 2.75;
      context.stroke();

      for (const point of points) {
        const selected = point.day === selectedDay;
        if (selected) {
          context.beginPath();
          context.arc(point.x, point.y, 9, 0, 2 * Math.PI);
          context.fillStyle = '#c1a3ff39';
          context.fill();
        }
        context.beginPath();
        context.arc(point.x, point.y, selected ? 4.7 : 3, 0, 2 * Math.PI);
        context.fillStyle = selected ? '#f0e7ff' : '#1b1e2a';
        context.fill();
        context.strokeStyle = accent;
        context.lineWidth = 1.6;
        context.stroke();
      }
    }

    const observer = new ResizeObserver(draw);
    observer.observe(chart);
    draw();
    return () => observer.disconnect();
  }, [rows, max, selectedDay]);

  return <canvas ref={canvas} className="sales-chart-plot" aria-hidden="true"/>;
}

function Trend({ rows }) {
  const [activeDay, setActiveDay] = useState(null);
  if (!rows?.length) return <p className="empty">Registra ventas para ver la tendencia.</p>;

  const peak = Math.max(1, ...rows.map(row => row.value));
  const interval = peak / 4;
  const magnitude = 10 ** Math.floor(Math.log10(interval));
  const step = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 7.5, 8, 10].find(size => size * magnitude >= interval) * magnitude;
  const max = step * 4;
  const selected = rows.find(row => row.day === activeDay) ?? rows.at(-1);

  return <div className="sales-chart" role="group" aria-label="Ventas por día">
    <div className="sales-chart-summary" aria-live="polite">
      <strong>{money.format(selected.value)}</strong>
      <time dateTime={selected.day}>{formatDay(selected.day)}</time>
    </div>
    <div className="sales-chart-frame">
      <div className="sales-chart-axis" aria-hidden="true">
        {[4, 3, 2, 1, 0].map(tick => <span key={tick}>{axisAmount.format(tick * step)}</span>)}
      </div>
      <div className="sales-chart-grid" aria-hidden="true"/>
      <SalesPlot rows={rows} max={max} selectedDay={selected.day}/>
      <div className="sales-chart-days">
        {rows.map(row => <button key={row.day} type="button" className="sales-chart-day"
          aria-label={formatDay(row.day) + ', ' + money.format(row.value)}
          aria-pressed={selected.day === row.day}
          onPointerEnter={() => setActiveDay(row.day)}
          onFocus={() => setActiveDay(row.day)}
          onClick={() => setActiveDay(row.day)}>
          <span className="sales-chart-hit" aria-hidden="true"/>
          <span className="sales-chart-date" aria-hidden="true">{row.label}</span>
        </button>)}
      </div>
    </div>
  </div>;
}

function Excel({ kind, submit, busy }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [stock, setStock] = useState(false);
  function body() {
    const form = new FormData();
    form.set('archivo', file);
    form.set('stock', String(stock));
    return form;
  }
  return <Card title="Importar y exportar Excel" actions={<div className="actions">
    <a className="button" href={'/api/plantilla/' + kind}>Plantilla</a>
    <a className="button" href={'/api/exportar/' + kind}>Exportar</a>
  </div>}>
    <form className="form-stack" onSubmit={e => {
      e.preventDefault();
      submit('validar/' + kind, body(), setPreview, false);
    }}>
      <Field label="Archivo de Excel"><input type="file" required accept=".xlsx" onChange={e => { setFile(e.target.files[0]); setPreview(null); }}/></Field>
      {kind !== 'productos' && <label className="check"><input type="checkbox" checked={stock} onChange={e => setStock(e.target.checked)}/> {kind === 'ventas' ? 'Descontar del stock' : 'Aumentar el stock'}</label>}
      <div className="actions"><button disabled={busy || !file}>Validar archivo</button>
      {preview && !preview.errors.length && preview.count > 0 && <button type="button" className="primary" disabled={busy} onClick={() => submit('importar/' + kind, body(), () => setPreview(null))}>Importar {preview.count} filas</button>}</div>
    </form>
    {preview && <>
      <Notice message={preview.count + ' filas válidas'}/>
      {preview.errors.length > 0 && <ul className="error-list">{preview.errors.map((error, i) => <li key={i}>{error}</li>)}</ul>}
      {objectTable(preview.rows)}
    </>}
  </Card>;
}

function Products({ rows, submit, busy, admin }) {
  const element = useRef(null);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let mounted = true;
    function fail() { setFailed(true); }
    window.addEventListener('humbertito-inventory-error', fail);
    customElements.whenDefined('humbertito-inventory').then(() => {
      if (mounted) setReady(true);
    });
    return () => {
      mounted = false;
      window.removeEventListener('humbertito-inventory-error', fail);
    };
  }, []);

  useEffect(() => {
    if (!ready || !element.current) return;
    element.current.rows = rows;
    element.current.submit = (path, data) => busy ? Promise.resolve(false) : submit(path, data);
  }, [ready, rows, submit, busy]);

  return <>
    <Script src="/angular-inventory/main.js" type="module" strategy="afterInteractive" onError={() => setFailed(true)}/>
    {failed && <Notice message="No se pudo cargar el inventario. Recarga la página para volver a intentarlo." error/>}
    {!ready && !failed && <p className="loading" role="status">Cargando inventario…</p>}
    {ready && <humbertito-inventory ref={element}/>}
    <Excel kind="productos" submit={submit} busy={busy}/>
    {admin && <Danger title="Vaciar catálogo" path="productos/vaciar" submit={submit} busy={busy}/>}
  </>;
}

function ProductSelect({ rows, onChange }) {
  return <select name="producto_id" required defaultValue="" onChange={onChange}>
    <option value="" disabled>Selecciona un producto</option>
    {rows.map(row => <option key={row.id} value={row.id}>{row.codigo} · {row.nombre} ({row.stock} en stock)</option>)}
  </select>;
}

function ImportAudit({ summary }) {
  const counts = value => integer.format(value ?? 0);
  const fields = [
    ['Compras', counts(summary.compras)],
    ['Total registrado', money.format(summary.total_encabezados ?? 0)],
    ['Total de detalles', money.format(summary.total_detalles ?? 0)],
    ['Líneas de compra', counts(summary.lineas)],
    ['Primera compra', formatDay(summary.primera_fecha)],
    ['Última compra', formatDay(summary.ultima_fecha)],
    ['Sin detalles', counts(summary.sin_detalles)],
    ['Compras con diferencias', counts(summary.diferencias)],
  ];

  return <dl className="audit-summary">
    {fields.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}
  </dl>;
}

function Movements({ kind, products, rows, audit, submit, busy, admin }) {
  const sale = kind === 'ventas';
  const word = sale ? 'venta' : 'compra';
  return <>
    <Card title={'Registrar ' + word}><form className="form-grid" onSubmit={e => {
      e.preventDefault();
      const form = e.currentTarget;
      const data = Object.fromEntries(new FormData(form));
      submit(kind + '/crear', { ...data, stock: data.stock === 'on' }, () => form.reset());
    }}>
      <Field label="Producto"><ProductSelect rows={products}/></Field>
      <Field label="Cantidad"><input type="number" name="cantidad" min="1" step="1" required/></Field>
      <Field label={sale ? 'Precio unitario (opcional)' : 'Precio unitario de compra'}><input type="number" name="precio" min="0.01" step="0.01" required={!sale}/></Field>
      {sale && <><Field label="Fecha"><input type="date" name="fecha" defaultValue={localDay.format(new Date())}/></Field>
        <label className="check full"><input type="checkbox" name="stock" defaultChecked/> Descontar del stock</label></>}
      <div className="actions full"><button className="primary" disabled={busy || !products.length}>Registrar {word}</button></div>
    </form></Card>
    <Card title={'Historial de ' + kind}><Table rows={rows} columns={movementColumns} searchable action={sale ? row =>
      <button type="button" className="danger" disabled={busy} onClick={() => {
        if (!window.confirm('¿Eliminar la venta #' + row.id + '?')) return;
        const restore = row.stock_descontado == null && window.confirm('Esta venta es anterior al control de existencias. ¿Devolver las unidades al stock?');
        submit('ventas/eliminar', { id: row.id, restaurar: restore });
      }}>Eliminar</button> : undefined}/></Card>
    <Excel kind={kind} submit={submit} busy={busy}/>
    {audit && <Card title="Auditoría de importaciones">
      <ImportAudit summary={audit.resumen ?? {}}/>
      {audit.archivos?.length > 0 && objectTable(audit.archivos.map(row => Object.fromEntries(row.map((value, index) => [['ID', 'Archivo', 'Fecha', 'Registros', 'Estado', 'Compras'][index] ?? ('Dato ' + index), value]))))}
    </Card>}
    {sale && admin && <Danger title="Vaciar historial de ventas" path="ventas/vaciar" submit={submit} busy={busy}/>}
  </>;
}

const percent = new Intl.NumberFormat('es-PE', {
  style: 'percent', maximumFractionDigits: 1, signDisplay: 'exceptZero',
});
const shortDate = new Intl.DateTimeFormat('es-PE', {
  day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC',
});
const modelStatuses = {
  ok: ['Modelo listo', 'Disponible para generar pronósticos.'],
  modelo_no_entrenado: ['Pendiente de entrenamiento', 'Entrena el modelo con el historial de ventas para generar pronósticos.'],
  modelo_desactualizado: ['Requiere actualización', 'Entrena y evalúa el modelo con el historial actual.'],
  modelo_invalido: ['Modelo no disponible', 'Vuelve a entrenarlo para generar pronósticos.'],
};

function formatDay(value) {
  if (!value) return '—';
  const date = new Date(String(value).slice(0, 10) + 'T00:00:00Z');
  return Number.isNaN(date.getTime()) ? '—' : shortDate.format(date);
}

function SalesTrend({ trend }) {
  const change = Number.isFinite(trend.valor) ? percent.format(trend.valor / 100) : '—';
  const hasPeriod = Boolean(trend.fecha_inicio && trend.fecha_fin);
  return <Card title="Tendencia de ventas">
    <div className="trend-summary">
      <strong className="trend-status">{trend.tipo}</strong>
      {hasPeriod && <span className="muted">{formatDay(trend.fecha_inicio)} – {formatDay(trend.fecha_fin)}</span>}
    </div>
    {hasPeriod && <dl className="trend-values">
      <div><dt>Ventas del periodo base</dt><dd>{money.format(trend.ventas_periodo_base)}</dd></div>
      <div><dt>Ventas del periodo reciente</dt><dd>{money.format(trend.ventas_periodo_reciente)}</dd></div>
      <div><dt>Variación</dt><dd className={trend.valor < 0 ? 'trend-negative' : undefined}>{change}</dd></div>
    </dl>}
    {hasPeriod && trend.dias_por_periodo > 0 && <p className="muted trend-period">{trend.dias_por_periodo} días por periodo</p>}
    {trend.explicacion && <p className="trend-explanation">{trend.explicacion}</p>}
  </Card>;
}

function Forecast({ products, model, submit, busy, admin }) {
  const [product, setProduct] = useState('');
  const [result, setResult] = useState(null);
  const [request, setRequest] = useState(null);
  const [evaluationOpen, setEvaluationOpen] = useState(false);
  const selected = products.find(row => String(row.id) === product);
  const [status, statusText] = modelStatuses[model?.estado] ?? ['Estado no disponible', 'Consulta el estado del modelo de demanda.'];
  return <>
    <Card title="Estado del modelo" actions={admin && <button className="button" disabled={busy} onClick={() => submit('modelo/entrenar', {}, data => setResult({ training: data }))}>Entrenar y evaluar</button>}>
      <div className="model-status">
        <span className={'pill' + (model?.estado === 'ok' ? '' : ' warning')}>{status}</span>
        <p className="muted">{statusText}</p>
      </div>
      {model?.evaluacion?.cortes_evaluacion?.length > 0 && <details open={evaluationOpen} onToggle={event => setEvaluationOpen(event.currentTarget.open)}>
        <summary>Evaluación por periodo</summary>
        <Table
          rows={model.evaluacion.cortes_evaluacion}
          columns={Object.keys(model.evaluacion.cortes_evaluacion[0]).map(key => [key, key.replaceAll('_', ' ')])}
          action={admin ? row => <button className="danger" type="button" disabled={busy}
            aria-label={'Eliminar evaluación del ' + formatDay(row.fecha_corte)}
            onClick={() => {
              if (window.confirm('¿Eliminar el registro de evaluación del ' + formatDay(row.fecha_corte) + '?')) {
                submit('modelo/evaluacion/eliminar', { fecha_corte: row.fecha_corte, confirmacion: row.fecha_corte });
              }
            }}>Eliminar</button> : undefined}
        />
      </details>}
      {result?.training && <Notice message={result.training.mensaje ?? 'Evaluación completada.'}/>}
    </Card>
    <Card title="Generar pronóstico"><form className="form-grid" onSubmit={e => {
      e.preventDefault();
      const fields = Object.fromEntries(new FormData(e.currentTarget));
      submit('pronostico', fields, data => { setResult(data); setRequest(fields); }, false);
    }}>
      <Field label="Producto"><ProductSelect rows={products} onChange={e => { setProduct(e.target.value); setResult(null); }}/></Field>
      <Field key={product} label="Días de cobertura"><input name="dias" type="number" required min={Math.max(1, selected?.dias_entrega ?? 0)} max="30" defaultValue={Math.max(7, selected?.dias_entrega ?? 0)}/></Field>
      <div className="actions full"><button className="primary" disabled={busy || !products.length}>Generar pronóstico</button></div>
    </form></Card>
    {result?.predicciones && <Card title="Demanda estimada" actions={<a className="button" href={'/api/pronostico/pdf?' + new URLSearchParams(request)}>Descargar PDF</a>}>
      <Metrics items={[
        ['Demanda total', integer.format(result.demanda_predicha), 'trending_up'],
        ['Promedio diario', integer.format(result.promedio_diario_predicho), 'show_chart'],
        ['Reposición sugerida', integer.format(result.reposicion), 'inventory_2'],
      ]}/>
      <Table columns={ [['fecha', 'Fecha'], ['unidades', 'Unidades estimadas']] } rows={result.predicciones.map((value, index) => ({ id: index, fecha: result.fechas_prediccion[index], unidades: integer.format(value) }))}/>
    </Card>}
  </>;
}

function Danger({ title, path, submit, busy }) {
  return <Card title={title}><form className="actions" onSubmit={e => {
    e.preventDefault();
    const form = e.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    if (window.confirm('¿Confirmas esta operación?')) submit(path, data, () => form.reset());
  }}>
    <Field label="Escribe CONFIRMAR"><input name="confirmacion" pattern="CONFIRMAR" required autoComplete="off"/></Field>
    <button type="submit" className="danger" disabled={busy}>Confirmar operación</button>
  </form></Card>;
}

function Users({ rows, user, submit, busy }) {
  return <>
    <Card title="Crear una cuenta"><form className="form-grid" onSubmit={e => {
      e.preventDefault();
      const form = e.currentTarget;
      submit('usuarios/crear', Object.fromEntries(new FormData(form)), () => form.reset());
    }}>
      <Field label="Nombre completo"><input name="nombre" required/></Field>
      <Field label="Usuario"><input name="username" required autoComplete="off"/></Field>
      <Field label="Contraseña"><input name="password" type="password" minLength={8} required autoComplete="new-password"/></Field>
      <Field label="Rol"><select name="rol"><option value="empleado">Empleado</option><option value="admin">Administrador</option></select></Field>
      <div className="actions full"><button className="primary" disabled={busy}>Crear cuenta</button></div>
    </form></Card>
    <Card title="Cuentas registradas"><Table rows={rows} columns={ [['nombre', 'Nombre'], ['username', 'Usuario'], ['rol', 'Rol'], ['creado', 'Creado']] } action={row => row.id !== user.id && <button className="danger" type="button" disabled={busy} onClick={() => {
      if (window.confirm('¿Eliminar la cuenta ' + row.username + '?')) submit('usuarios/eliminar', { id: row.id });
    }}>Eliminar</button>}/></Card>
    {rows.some(row => row.id !== user.id) && <Card title="Transferir administración"><form className="actions" onSubmit={e => {
      e.preventDefault();
      if (window.confirm('¿Transferir la administración y eliminar tu cuenta actual?')) submit('usuarios/transferir', Object.fromEntries(new FormData(e.currentTarget)), undefined, false);
    }}>
      <Field label="Cuenta que recibirá la administración"><select name="id" required defaultValue=""><option value="" disabled>Selecciona una cuenta</option>
        {rows.filter(row => row.id !== user.id).map(row => <option key={row.id} value={row.id}>{row.nombre}</option>)}</select></Field>
      <button className="danger" disabled={busy}>Transferir y eliminar mi cuenta</button>
    </form></Card>}
    <Danger title="Reiniciar datos operativos" path="reiniciar" submit={submit} busy={busy}/>
  </>;
}

function Brand() {
  return <div className="brand">
    <span className="brand-mark"><Icon name="menu_book"/></span>
    <div><small>Sistema de gestión</small><strong>Librería Bazar Humbertito</strong></div>
  </div>;
}

function Login({ notice, busy, onLogin }) {
  const [showPassword, setShowPassword] = useState(false);

  return <main className="access">
    <section className="login" aria-labelledby="login-title">
      <div className="login-intro">
        <Brand/>
        <h2>Gestiona tu librería</h2>
        <p>Registra ventas, controla el stock y consulta tus compras desde el mismo lugar.</p>
        <ul className="login-modules" aria-label="Módulos del sistema">
          <li><Icon name="inventory_2"/>Inventario</li>
          <li><Icon name="point_of_sale"/>Ventas</li>
          <li><Icon name="shopping_cart"/>Compras</li>
        </ul>
      </div>
      <div className="login-content">
        <header className="login-heading">
          <p className="eyebrow">Acceso al sistema</p>
          <h1 id="login-title">Iniciar sesión</h1>
          <p>Ingresa con la cuenta de tu librería.</p>
        </header>
        <Notice {...notice}/>
        <form className="form-stack" onSubmit={event => {
          event.preventDefault();
          onLogin(Object.fromEntries(new FormData(event.currentTarget)));
        }}>
          <Field label="Usuario"><input name="username" autoComplete="username" required/></Field>
          <div className="field">
            <label className="field-label" htmlFor="login-password">Contraseña</label>
            <div className="password-field">
              <input id="login-password" name="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" required/>
              <button type="button" aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'} aria-controls="login-password"
                onClick={() => setShowPassword(value => !value)}>
                {showPassword ? <EyeOff size={19} aria-hidden="true"/> : <Eye size={19} aria-hidden="true"/>}
              </button>
            </div>
          </div>
          <button className="primary login-submit" disabled={busy}>
            <LogIn size={19} aria-hidden="true"/>{busy ? 'Ingresando…' : 'Iniciar sesión'}
          </button>
        </form>
      </div>
    </section>
  </main>;
}

export default function Page() {
  const [user, setUser] = useState(undefined);
  const [screen, setScreen] = useState('resumen');
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  const [notice, setNotice] = useState(null);
  const [drawer, setDrawer] = useState(false);

  const fail = useCallback(error => {
    if (error.status === 401) setUser(null);
    setNotice({ error: true, message: [error.message, ...(error.details ?? [])].join(' ') });
  }, []);

  useEffect(() => {
    call('sesion').then(setUser).catch(error => {
      setUser(null);
      if (error.status !== 401) fail(error);
    });
  }, [fail]);

  useEffect(() => {
    if (!user) return;
    let active = true;
    setLoading(true);
    const routes = {
      resumen: ['resumen', 'ventas'], productos: ['productos'], ventas: ['ventas', 'productos'],
      compras: ['compras', 'productos', 'compras/auditoria'], analisis: ['analisis'],
      modelo: ['modelo', 'productos'], usuarios: ['usuarios'],
    }[screen];
    Promise.all(routes.map(async path => [path, await call(path)]))
      .then(results => { if (active) setData(Object.fromEntries(results)); })
      .catch(error => { if (active) fail(error); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [user, screen, revision, fail]);

  async function submit(path, body, onSuccess, refresh = true) {
    setBusy(true);
    setNotice(null);
    try {
      const result = await call(path, body);
      onSuccess?.(result);
      if (path === 'salir' || path === 'usuarios/transferir') { setData({}); setUser(null); }
      if (result.message) setNotice({ message: result.message });
      if (refresh) setRevision(value => value + 1);
      return true;
    } catch (error) {
      fail(error);
      return false;
    } finally {
      setBusy(false);
    }
  }

  if (user === undefined) return <main className="access"><div role="status">Cargando Humbertito…</div></main>;
  if (!user) return <Login notice={notice} busy={busy} onLogin={data =>
    submit('entrar', data, account => { setScreen('resumen'); setUser(account); }, false)
  }/>;

  const admin = user.rol === 'admin';
  const active = sections.find(([key]) => key === screen);
  const dashboard = data.resumen ?? {};
  const daily = new Map();
  for (const row of data.ventas ?? []) {
    const day = String(row.fecha ?? '').slice(0, 10);
    if (day) daily.set(day, (daily.get(day) ?? 0) + Number(row.subtotal));
  }
  const trend = [...daily].sort(([a], [b]) => a.localeCompare(b)).slice(-10).map(([day, value]) => ({ day, label: day.slice(5).split('-').reverse().join('/'), value }));
  const props = { submit, busy, admin };
  return <div className="shell">
    <aside className={drawer ? 'sidebar open' : 'sidebar'}>
      <Brand/>
      <nav aria-label="Módulos">{navigation.map(([group, entries]) => {
        const allowed = entries.filter(([key]) => key !== 'usuarios' || admin);
        if (!allowed.length) return null;
        return <div className="nav-group" key={group} role="group" aria-label={group}>
          <span className="nav-group-label" aria-hidden="true">{group}</span>
          {allowed.map(([key, label, icon]) =>
            <button key={key} type="button" aria-current={key === screen ? 'page' : undefined} onClick={() => {
              if (busy) return;
              if (screen !== key) { setData({}); setLoading(true); }
              setScreen(key); setNotice(null); setDrawer(false);
            }}><Icon name={icon}/>{label}</button>)}
        </div>;
      })}</nav>
      <div className="account"><div><strong>{user.nombre}</strong><small>{admin ? 'Administración' : 'Operaciones'}</small></div>
        <button title="Cerrar sesión" aria-label="Cerrar sesión" type="button" disabled={busy} onClick={() => submit('salir', {}, undefined, false)}><Icon name="logout"/></button></div>
    </aside>
    <main className="workspace">
      <header className="topbar"><button className="nav-toggle" type="button" aria-label="Menú" aria-expanded={drawer} onClick={() => setDrawer(!drawer)}><Icon name="menu"/></button>
        <span className="top-title">Librería Bazar Humbertito</span>
        <span className="top-date">{new Intl.DateTimeFormat('es-PE', { dateStyle: 'medium', timeZone: 'America/Lima' }).format(new Date())}</span>
      </header>
      <div className="main-content">
        <div className="workspace-heading">
          <span className="workspace-icon"><Icon name={active[2]}/></span>
          <h1>{active[1]}</h1>
        </div>
        <Notice {...notice}/>
        {loading && <p className="loading" role="status">Actualizando datos…</p>}
        {!loading && screen === 'resumen' && data.resumen && <>
          <Metrics items={[
            ['Ventas acumuladas', money.format(dashboard.ventas), 'point_of_sale'],
            ['Compras acumuladas', money.format(dashboard.compras), 'shopping_cart'],
            ['Productos registrados', integer.format(dashboard.productos), 'inventory_2'],
            ['Productos con stock bajo', integer.format(dashboard.stock_bajo), 'warning'],
          ]}/>
          <div className="dashboard-grid">
            <Card title="Ventas por día"><Trend rows={trend}/></Card>
            <Card title="Alertas de stock"><Table rows={dashboard.alertas} columns={ [['nombre', 'Producto'], ['stock', 'Stock'], ['stock_minimo', 'Mínimo']] }/></Card>
          </div>
          <Card title="Movimientos recientes"><Table rows={(data.ventas ?? []).slice(0, 6)} columns={movementColumns}/></Card>
        </>}
        {screen === 'productos' && data.productos && <Products rows={data.productos} {...props}/>}
        {(screen === 'ventas' || screen === 'compras') && data[screen] && <Movements key={screen} kind={screen} products={data.productos} rows={data[screen]} audit={data['compras/auditoria']} {...props}/>}
        {screen === 'analisis' && data.analisis && <>
          <Metrics items={[
            ['Ventas totales', money.format(data.analisis.resumen.total_ventas), 'point_of_sale'],
            ['Unidades vendidas', integer.format(data.analisis.resumen.unidades_vendidas), 'inventory_2'],
            ['Promedio de ventas por día', money.format(data.analisis.resumen.promedio_diario), 'monitoring'],
            ['Días con ventas', integer.format(data.analisis.resumen.dias_con_ventas), 'dashboard'],
          ]}/>
          <SalesTrend trend={data.analisis.tendencia}/>
          <Card title="Productos más vendidos">{objectTable(data.analisis.destacados)}</Card>
          <Card title="Análisis por producto">{objectTable(data.analisis.productos)}</Card>
          <Card title="Alertas en importes diarios">{objectTable(data.analisis.alertas)}</Card>
        </>}
        {screen === 'modelo' && data.productos && <Forecast products={data.productos} model={data.modelo} {...props}/>}
        {screen === 'usuarios' && admin && data.usuarios && <Users rows={data.usuarios} user={user} {...props}/>}
        {!loading && !Object.keys(data).length && notice?.error && <button type="button" onClick={() => setRevision(value => value + 1)}>Reintentar</button>}
      </div>
    </main>
  </div>;
}
