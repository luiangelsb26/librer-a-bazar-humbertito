'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

const sections = [
  ['resumen', 'Vista general', 'dashboard'],
  ['productos', 'Inventario', 'inventory_2'],
  ['ventas', 'Ventas', 'point_of_sale'],
  ['compras', 'Compras', 'shopping_cart'],
  ['analisis', 'Análisis comercial', 'monitoring'],
  ['modelo', 'Pronóstico', 'trending_up'],
  ['usuarios', 'Administración', 'manage_accounts'],
];
const money = new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' });
const integer = new Intl.NumberFormat('es-PE', { maximumFractionDigits: 2 });
const localDay = new Intl.DateTimeFormat('sv-SE', { timeZone: 'America/Lima' });
const productFields = [
  ['codigo', 'Código'], ['nombre', 'Nombre'], ['categoria', 'Categoría'],
  ['precio_compra', 'Precio de compra', 'money'], ['precio_venta', 'Precio de venta', 'money'],
  ['stock', 'Existencias', 'integer'], ['stock_minimo', 'Stock mínimo', 'integer'],
  ['dias_entrega', 'Plazo de entrega en días', 'integer'],
];
const productColumns = [
  ['codigo', 'Código'], ['nombre', 'Producto'], ['categoria', 'Categoría'],
  ['precio_compra', 'Compra', 'money'], ['precio_venta', 'Venta', 'money'],
  ['stock', 'Existencias'], ['stock_minimo', 'Mínimo'], ['dias_entrega', 'Entrega (días)'],
];
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

function Icon({ name }) {
  return <span className="material-symbols-outlined icon" aria-hidden="true">{name}</span>;
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

function Trend({ rows }) {
  if (!rows?.length) return <p className="empty">Registra ventas para ver la tendencia.</p>;
  const max = Math.max(1, ...rows.map(row => Number(row.value)));
  return <div className="trend" aria-label="Gráfico de ventas">
    {rows.map((row, index) => <div className="bar-column" key={index} title={row.label + ' · ' + money.format(row.value)}>
      <div className="bar-track"><div style={{ height: (100 * Number(row.value) / max) + '%' }}/></div>
      <span>{row.label}</span>
    </div>)}
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
  const [edit, setEdit] = useState(null);
  return <>
    <Card title={edit ? 'Editar producto' : 'Registrar producto'}>
      <form key={edit?.id ?? 'new'} className="form-grid" onSubmit={e => {
        e.preventDefault();
        const form = e.currentTarget;
        const data = Object.fromEntries(new FormData(form));
        submit(edit ? 'productos/editar' : 'productos/crear', { ...data, id: edit?.id }, () => { form.reset(); setEdit(null); });
      }}>
        {productFields.map(([key, label, format]) => <Field key={key} label={label}>
          <input name={key} defaultValue={edit?.[key] ?? (format ? 0 : '')} type={format ? 'number' : 'text'} step={format === 'money' ? '0.01' : undefined} min={key === 'precio_venta' ? '0.01' : (format ? 0 : undefined)}
            max={key === 'dias_entrega' ? 30 : undefined} maxLength={format ? undefined : 250} required={key !== 'categoria'}/>
        </Field>)}
        <div className="actions full"><button className="primary" disabled={busy}>{edit ? 'Guardar cambios' : 'Registrar producto'}</button>
          {edit && <button type="button" onClick={() => setEdit(null)}>Cancelar</button>}</div>
      </form>
    </Card>
    <Card title="Productos registrados"><Table rows={rows} columns={productColumns} searchable action={row => <>
      <button type="button" onClick={() => { setEdit(row); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>Editar</button>
      <button type="button" className="danger" disabled={busy} onClick={() => {
        if (window.confirm('¿Eliminar el producto ' + row.nombre + '?')) submit('productos/eliminar', { id: row.id });
      }}>Eliminar</button>
    </>}/></Card>
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
      <Metrics items={Object.entries(audit.resumen ?? {}).map(([key, value]) => [key.replaceAll('_', ' '), value])}/>
      {audit.archivos?.length > 0 && objectTable(audit.archivos.map(row => Object.fromEntries(row.map((value, index) => [['ID', 'Archivo', 'Fecha', 'Registros', 'Estado', 'Compras'][index] ?? ('Dato ' + index), value]))))}
    </Card>}
    {sale && admin && <Danger title="Vaciar historial de ventas" path="ventas/vaciar" submit={submit} busy={busy}/>}
  </>;
}

function Forecast({ products, model, submit, busy, admin }) {
  const [product, setProduct] = useState('');
  const [result, setResult] = useState(null);
  const [request, setRequest] = useState(null);
  const selected = products.find(row => String(row.id) === product);
  return <>
    <Card title="Estado del modelo" actions={admin && <button className="button" disabled={busy} onClick={() => submit('modelo/entrenar', {}, data => setResult({ training: data }))}>Entrenar y evaluar</button>}>
      <p className="muted">{model?.mensaje ?? 'Consulta el estado del modelo de demanda.'}</p>
      {model?.algoritmo && <span className="pill">{model.algoritmo}</span>}
      {model?.evaluacion?.cortes_evaluacion && <details><summary>Evaluación por periodo</summary>{objectTable(model.evaluacion.cortes_evaluacion)}</details>}
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
  return <div className="brand"><span><Icon name="menu_book"/></span><div><strong>Humbertito</strong><small>Librería y bazar</small></div></div>;
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
    } catch (error) {
      fail(error);
    } finally {
      setBusy(false);
    }
  }

  if (user === undefined) return <main className="access"><div role="status">Cargando Humbertito…</div></main>;
  if (!user) return <main className="access"><section className="login">
    <Brand/><h1>Iniciar sesión</h1>
    <Notice {...notice}/>
    <form className="form-stack" onSubmit={e => {
      e.preventDefault();
      submit('entrar', Object.fromEntries(new FormData(e.currentTarget)), account => { setScreen('resumen'); setUser(account); }, false);
    }}>
      <Field label="Usuario"><input name="username" autoComplete="username" required/></Field>
      <Field label="Contraseña"><input name="password" type="password" autoComplete="current-password" required/></Field>
      <button className="primary" disabled={busy}>{busy ? 'Ingresando…' : 'Entrar al sistema'}</button>
    </form>
  </section></main>;

  const admin = user.rol === 'admin';
  const active = sections.find(([key]) => key === screen);
  const dashboard = data.resumen ?? {};
  const daily = new Map();
  for (const row of data.ventas ?? []) {
    const day = String(row.fecha ?? '').slice(0, 10);
    if (day) daily.set(day, (daily.get(day) ?? 0) + Number(row.subtotal));
  }
  const trend = [...daily].sort(([a], [b]) => a.localeCompare(b)).slice(-10).map(([day, value]) => ({ label: day.slice(5).split('-').reverse().join('/'), value }));
  const props = { submit, busy, admin };
  return <div className="shell">
    <aside className={drawer ? 'sidebar open' : 'sidebar'}>
      <Brand/>
      <nav aria-label="Módulos">{sections.filter(([key]) => key !== 'usuarios' || admin).map(([key, label, icon]) =>
        <button key={key} type="button" aria-current={key === screen ? 'page' : undefined} onClick={() => {
          if (busy) return;
          if (screen !== key) { setData({}); setLoading(true); }
          setScreen(key); setNotice(null); setDrawer(false);
        }}><Icon name={icon}/>{label}</button>)}</nav>
      <div className="account"><div><strong>{user.nombre}</strong><small>{admin ? 'Administración' : 'Operaciones'}</small></div>
        <button title="Cerrar sesión" aria-label="Cerrar sesión" type="button" disabled={busy} onClick={() => submit('salir', {}, undefined, false)}><Icon name="logout"/></button></div>
    </aside>
    <main className="workspace">
      <header className="topbar"><button className="nav-toggle" type="button" aria-label="Menú" aria-expanded={drawer} onClick={() => setDrawer(!drawer)}><Icon name="menu"/></button>
        <span>Librería Bazar Humbertito</span>
        <span className="top-date">{new Intl.DateTimeFormat('es-PE', { dateStyle: 'medium', timeZone: 'America/Lima' }).format(new Date())}</span>
      </header>
      <div className="main-content">
        <h1>{active[1]}</h1>
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
          <Metrics items={Object.entries(data.analisis.resumen).filter(([, value]) => typeof value === 'number').map(([key, value]) => [key.replaceAll('_', ' '), integer.format(value), 'query_stats'])}/>
          <Card title="Tendencia de ventas"><Metrics items={Object.entries(data.analisis.tendencia).filter(([, value]) => ['number', 'string'].includes(typeof value)).map(([key, value]) => [key.replaceAll('_', ' '), typeof value === 'number' ? integer.format(value) : value])}/></Card>
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
