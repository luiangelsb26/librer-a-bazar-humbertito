import './styles.css';

export const metadata = {
  title: 'Humbertito | Gestión de librería y bazar',
  description: 'Inventario, compras, ventas y pronóstico de demanda',
};

export default function Layout({ children }) {
  return <html lang="es-PE"><body>{children}</body></html>;
}
